from flask import session, redirect, url_for, render_template, current_app, flash, request, abort, make_response
from flask_login import current_user, login_required

from . import main
from .forms import NameForm, EditProfileForm, AdminEditProfileForm, PostForm
from ..email import send_email
from .. import db
from ..models import Role, User, Permission, Post, Follow
from ..decorators import admin_require
from ..decorators import permission_require


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user._get_current_object())
        db.session.add(post)
        flash('The post you write has been committed.')
        return redirect(url_for('.index'))
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
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination)


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
        flash('Your profile has been update.')
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
        flash('The profile has been updated.')
        return redirect(url_for('.user'), username=user.username)
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed = user.confirmed
    form.role.data = user.role.name
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


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
        flash('The post has been update.')
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
        flash('Invalid username.')
        return redirect(url_for(('.index')))
    if current_user.is_following(user):
        flash('You are already following the user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_require(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid username')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following the user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore' % username)
    return redirect('.user', username=username)


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid username.')
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
        flash('Invalid username.')
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
