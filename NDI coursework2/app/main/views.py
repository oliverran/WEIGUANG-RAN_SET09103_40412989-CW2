#-*- coding:utf-8 -*-
from app.forms import LoginForm, BaseEntryForm
from app.models import Item
from app.util import TypeRender
from collections import defaultdict
from flask import render_template, request, flash, url_for, abort, redirect, jsonify
from flask.ext.login import current_user, login_required

from . import main
import re

@main.route('/')
def index():
    lg_form = LoginForm()
    return render_template('index.html', lg_form=lg_form, title='index')

pk_regx = re.compile(r'(\w+)\s+(pk|Pk|pK|PK)\s+(\w+)', re.IGNORECASE)

@main.route('/pk', methods=['GET', 'POST'])
def pk():
    if request.method == 'POST':
        pk_str = request.form.get('pk').strip()
        g = pk_regx.match(pk_str)
        if g:
            pk1_title = g.groups()[0]
            pk2_title = g.groups()[2]
            pk1_regx = re.compile(pk1_title, re.IGNORECASE)
            pk2_regx = re.compile(pk2_title, re.IGNORECASE)
            pk1_item = Item.find_item(pk1_regx)
            pk2_item = Item.find_item(pk2_regx)
            if pk1_item and pk2_item:
                # 按首字母大小排序
                rows_by_name = defaultdict(list)
                for attr in pk1_item['attributes']:
                    rows_by_name[attr['attr_name']].append(attr)
                for attr in pk2_item['attributes']:
                    # 保证顺序
                    if not attr['attr_name'] in rows_by_name.keys():
                        rows_by_name[attr['attr_name']].append({})
                    rows_by_name[attr['attr_name']].append(attr)

                for key, attrs in rows_by_name.items():
                    if len(attrs) == 1:
                        attrs.append({})

                return render_template('pk.html', pk1=pk1_item, pk2=pk2_item,\
                                       rows=rows_by_name, TypeRender=TypeRender)
            else:
                if not pk1_item:
                    flash('cannot search the result%s'%pk1_title, 'red')
                if not pk2_item:
                    flash('cannot search the result%s'%pk2_title, 'red')
        else:
            flash('input the wrong format', 'red')
    return redirect(url_for('.index'))

@main.route('/explore')
def explore():
    items = Item.find_items()
    return render_template('explore.html', items=items, title='finding')

@main.route('/random')
def lucky():
    # 总条数
    item = Item.get_random_item()
    if item:
        return redirect(url_for('.item', title=item['title']))
    return redirect(url_for('.index'))

@main.route('/search')
def search():
    q = request.args.get('q', None)
    if q is None:
        abort(404)
    keyword = q.strip()
    regx = re.compile(r'%s' %keyword, re.IGNORECASE)
    list = Item.find_items(regx)
    if list.count() == 0:
        flash('no results', 'search')
    return render_template('explore.html', items=list, title='Searching')

@main.route('/item/<title>')
def item(title):
    item = Item.find_item(title)
    if not item:
        abort(404)
    Item.inc_view(title)
    return render_template('item.html', item=item, TypeRender=TypeRender)

@main.route('/item/edit_attr', methods=['POST'])
def edit_attr():
    if request.method == 'POST':
        title = request.json['title']
        attr_name = request.json['attr_name'].strip()
        attr_type = request.json['attr_type']
        attr_value = request.json['attr_value'].strip()
        if not attr_name:
            return jsonify(status=False, reason="Property name cannot be empty")
        if not attr_value:
            return jsonify(status=False, reason="Property name cannot be empty")
        status = Item.edit_attr(title, attr_name, attr_value, attr_type)
        if status:
            if current_user.is_authenticated:
                current_user.add_edit()
            return jsonify(status=True, reason="Edit succeed")
        else:
            return jsonify(status=True, reason="Edit fail")

@main.route('/item/del_attr', methods=['POST'])
@login_required
def del_attr():
    if request.method == 'POST':
        title = request.json['title']
        attr_name = request.json['attr_name']
        status = Item.del_attr(title, attr_name)
        if status:
            return jsonify(status=True, reason="delete attribute succeed")
        else:
            return jsonify(status=True, reason="delete attribute failure")

@main.route('/item/add_attr', methods=['POST'])
def add_attr():
    if request.method == 'POST':
        title = request.json['title']
        attr_name = request.json['attr_name'].strip()
        attr_type = request.json['attr_type']
        attr_value = request.json['attr_value'].strip()
        if not attr_name:
            return jsonify(status=False, reason="Property name cannot be empty")
        if not attr_value:
            return jsonify(status=False, reason="Property name cannot be empty")
        if Item.find_attr(title, attr_name) is not None:
            return jsonify(status=False, reason="Attributes have been existed")
        status = Item.add_attr(title, attr_name, attr_value, attr_type)
        if status:
            if current_user.is_authenticated:
                current_user.add_edit()
        html = TypeRender.render_html(attr_name, attr_value, attr_type)
        return jsonify(status=True, reason="Add attributes successfully", html=html)

@main.route('/create_entry', methods=['GET', 'POST'])
def create_entry():
    entry_form = BaseEntryForm()
    if entry_form.validate_on_submit():
        title = request.form['title'].strip()
        type = request.form['type'].strip()
        if not title:
            flash('Property name cannot be empty', 'red')
        elif not type:
            flash('Types cannot be empty', 'red')
        elif Item.find_item(title):
            flash('Entry has been existed', 'yellow')
        else:
            status = Item.create_item(title, type)
            if status:
                Item.add_type(type)
                if current_user.is_authenticated:
                    current_user.add_create()
            return redirect(url_for('.item', title=title))
    else:
        for field, errors in entry_form.errors.items():
            for error in errors:
                flash("%s: %s" %(getattr(entry_form, field).label.text, error), 'red')
    types = Item.types()
    return render_template('create.html', entry_form=entry_form, title='create the entry', types=types)

