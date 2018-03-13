# -*- coding: utf8 -*-

from flask import session, redirect, url_for, render_template, current_app, flash, request, abort, make_response
from flask_login import current_user, login_required

from . import main
from .forms import NameForm, EditProfileForm, AdminEditProfileForm, PostForm, CommentForm
from ..email import send_email
from .. import db
from ..models import Role, User, Permission, Post, Follow, Comment
from ..decorators import admin_require
from ..decorators import permission_require


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
            flash('评论提交成功')
            return redirect(url_for('.post', id=id, page=-1))
        else:
            abort(403)
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
        db.session.add(post)
        db.session.commit()
        flash('新的文章已提交')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit_post.html', form=form)


@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('文章修改成功')
        return redirect(url_for('.post', id=id))
    form.title.data = post.title
    form.content.data = post.content
    return render_template('edit_post.html', form=form)


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
    print pagination.items
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
