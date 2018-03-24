# -*- coding: utf8 -*-

import json
from flask import session, redirect, url_for, render_template, current_app, flash, request, abort, make_response
from flask_login import current_user, login_required

from . import main
from .forms import NameForm, EditProfileForm, AdminEditProfileForm, PostForm, CommentForm
from ..email import send_email
from .. import db
from ..models import Role, User, Permission, Post, Follow, Comment, Tag, Category
from ..decorators import admin_require
from ..decorators import permission_require
import flask_whooshalchemyplus
import copy


@main.route('/', methods=['GET', 'POST'])
def index():
    # form = PostForm()
    # if current_user.can(Permission.WRITE) and form.validate_on_submit():
    #     post = Post(title=form.title.data, content=form.content.data, author=current_user._get_current_object())
    #     db.session.add(post)
    #     flash('The post you write has been committed.')
    #     return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('您的个人资料已修改')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data =current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_require
def admin_edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditProfileForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.filter_by(name=form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('用户%s的个人资料已修改'%user.username)
        return redirect(url_for('.user'), username=user.username)
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed = user.confirmed
    form.role.data = user.role.name
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated and current_user.can(Permission.COMMENT):
            comment_content = form.content.data
            comment = Comment(content=comment_content, post=post, author=current_user._get_current_object())
            db.session.add(comment)
            db.session.commit()
            post.postviews -= 1    # 减1忽略评论后的跳转到文章页面的阅读次数
            flash('评论提交成功')
            return redirect(url_for('.post', id=id, page=-1))
        else:
            abort(403)
    post.postviews += 1    #只有 get 的阅读数加1， post的忽略
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.created_at.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False
    )
    comments = pagination.items
    return render_template('post.html', posts=[post], comments=comments, pagination=pagination, form=form)


@main.route('/edit_post', methods=['GET', 'POST'])
@login_required
@permission_require(Permission.WRITE)
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)
        #tag = []
        #for tag in form.tags.data.split(','):
        #if tag:
        print '*' * 40, post.tags
        tag_str_list = form.tags.data.split(',')
        for tag_str in tag_str_list:
            tag = Tag.query.filter_by(name=tag_str).first()
            if not tag:     # new post tag
                tag = Tag(name=tag_str)
                db.session.add(tag)
            post.tags.append(tag)
        category = Category.query.filter_by(name=form.category.data).first()
        if not category:
            category = Category(name=form.category.data)
            db.session.add(category)
        post.category = category
        db.session.add(post)
        db.session.commit()
        #with app.app_context():
        flask_whooshalchemyplus.index_one_model(Post)
        flash('新的文章已提交')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', post_commit_button=True, form=form)


@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data

        #old_tags = post.tags
        remove_tags = []
        tag_str_list = form.tags.data.split(',')
        for tag in post.tags:
            if tag.name not in tag_str_list:
                post.tags.remove(tag)
                remove_tags.append(tag)
        for tag_str in tag_str_list:
            tag = Tag.query.filter_by(name=tag_str).first()
            if not tag:     # new post tag
                tag = Tag(name=tag_str)
                db.session.add(tag)
            if not tag in post.tags:
                post.tags.append(tag)
        for tag in remove_tags:
            if tag.posts.count() == 0:
                print 'delete tag: %s because there is not any post use this tag' % tag.name
                db.session.delete(tag)

        if form.category.data != post.category.name:
            old_category = post.category
            category = Category.query.filter_by(name=form.category.data).first()
            if not category:
                category = Category(name=form.category.data)
                db.session.add(category)
            post.category = category
            #print old_category.name, old_category.posts.count()
            if old_category.posts.count() == 0:
                print 'delete category: %s because there is not any post in this category' % old_category.name
                db.session.delete(old_category)
        #post.tags.data = form.tags.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flask_whooshalchemyplus.index_one_model(Post)
        flash('文章修改成功')
        return redirect(url_for('.post', id=id))
    form.title.data = post.title
    form.tags.data = ','.join(tag.name for tag in post.tags)
    form.category.data = post.category.name
    form.content.data = post.content
    return render_template('edit_post.html', post_id=id, post_commit_button=True, form=form)


@main.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author_id != current_user.id and not current_user.is_administrator():
        abort(403)
    if post.comments.count() > 0:
        for comment in post.comments.all():
            db.session.delete(comment)

    remove_tags = []
    for tag in post.tags:
        post.tags.remove(tag)
        remove_tags.append(tag)
    for tag in remove_tags:
        if tag.posts.count() == 0:
            print 'delete tag: %s because there is not any post use this tag' % tag.name
            db.session.delete(tag)
    #old_tags = post.tags.all()
    old_category = post.category

    db.session.delete(post)

    # for old_tag in old_tags:
    #     if old_tag.posts.count() == 0:
    #         print 'delete tag: %s because there is not any post use this tag' % old_tag.name
    #         db.session.delete(old_tag)
    if old_category.posts.count() == 0:
        print 'delete category: %s because there is not any post in this category' % old_category.name
        db.session.delete(old_category)


    return redirect(url_for('.user', username=current_user.username))


@main.route('/follow/<username>')
@login_required
@permission_require(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for(('.index')))
    if current_user.is_following(user):
        flash('您已关注该用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('关注%s成功' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_require(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('您未关注该用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('取消关注 %s 成功' % username)
    return redirect('.user', username=username)


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.follow_time.desc()).paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False
    )
    #print pagination.items, type(pagination.items[0]), type(user.followers.all()[0])
    # user.followers.all() returns list of Follow object
    follows = [ { 'user': item.follower, 'follow_time': item.follow_time} for item in pagination.items ]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='.followers', follows=follows, pagination=pagination)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.follow_time.desc()).paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False
    )
    #print pagination.items
    follows = [ { 'user': item.followed, 'follow_time': item.follow_time} for item in pagination.items ]
    return render_template('followers.html', user=user, title='Followed of',
                           endpoint='.followed_by', follows=follows, pagination=pagination)


@main.route('/all')
@login_required
def show_all():
    response = make_response(redirect(url_for('.index')))
    response.set_cookie('show_followed', '', max_age=30*24*60*60)
    return response


@main.route('/followed')
@login_required
def show_followed():
    response = make_response(redirect(url_for('.index')))
    response.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return response


@main.route('/moderate')
@login_required
@permission_require(Permission.MODERATE)
def moderate_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_require(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate_comments', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_require(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate_comments', page=request.args.get('page', 1, type=int)))


@main.route('/apis')
@login_required
def get_apis():
    return render_template('api.html')


# jQuery ajax part load method to frontend
@main.route("/search")
def keyword_search():
    keyword = request.args.get('q')
    results = Post.query.whoosh_search(keyword,fields=['content'],limit=20).all()
    # or
    #results = Post.query.filter(...).msearch(keyword,fields=['title'],limit=20).filter(...)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.whoosh_search(keyword,fields=['content']).order_by(Post.created_at.desc()).paginate(
        page, per_page=current_app.config['SEARCH_RESULT_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('search.html', posts=posts,  results_number=len(results), show_followed=show_followed, pagination=pagination)

