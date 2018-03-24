from . import inner_api
from flask_login import login_required, current_user
from ..models import Post, Category, Tag
from flask import render_template, request, abort

import json


@inner_api.before_request
@login_required
def login_before_request():
    print 'in inner_api login_before_request'
    #if not current_user.is_authenticated:
    #    abort(403)


@inner_api.route('/get_post_content/<int:id>')
#@login_required
def get_post_content(id):
    if id == 0:
        return ''
    post = Post.query.get_or_404(id)
    return post.content


@inner_api.route('/categories')
@inner_api.route('/category/<int:post_id>')
#@login_required
def get_all_categories(post_id=None):
    search = request.args.get('q', None)
    if post_id is not None:
        categories = Post.query.get(post_id).category.all()
    elif search is None:
        categories = Category.query.all()
    else:
        search_like = '%%%s%%' % search
        categories = Category.query.filter(Category.name.like(search_like))
    data = [ dict(id=i, text=v.name) for i, v in enumerate(categories) ]
    #print type(categories), categories, repr(categories)
    #print json.dumps(repr(categories))
    return json.dumps(data)


@inner_api.route('/tags')
@inner_api.route('/tags/<int:post_id>')
#@login_required
def get_all_tags(post_id=None):
    search = request.args.get('q', None)
    if post_id is not None:
        tags = Post.query.get(post_id).tags.all()
    elif search is None:
        tags = Tag.query.all()
    else:
        search_like = '%%%s%%' % search
        tags = Tag.query.filter(Tag.name.like(search_like))
    data = [ dict(id=i, text=v.name) for i, v in enumerate(tags) ]
    print data
    #print type(categories), categories, repr(categories)
    #print json.dumps(repr(categories))
    return json.dumps(data)
#
# @inner_api.route('/test_tags')
# #@login_required
# def test_tags():
#     return render_template('test_tags.html')
#
# @inner_api.route('/test')
# #@login_required
# def test():
#     return render_template('test.html')