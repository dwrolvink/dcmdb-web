""" Blueprint module to serve /api/v1/ routes """
from ..integrator import Integrator
index = Integrator() 
backend = index.backend

from flask import request, redirect, url_for, jsonify

# Initialize Blueprint
apiv1 = index.Blueprint('api/v1', __name__)

# Globals
def url(url):
    return '/api/v1/' + url

def init_globals(g, title):
    g.title = title
    g.url = url
    g.host = request.host_url


# -- Routes
@apiv1.route('/api/v1/')
def render_homepage():
    init_globals(index.g, 'API v1 Documentation')
    return index.render_template('api_v1/home.html') 
 
@apiv1.route('/api/v1/docs/post/<object_type>/')
def render_post_docs(object_type):
    init_globals(index.g, 'API v1 Documentation - POST calls for {}'.format(object_type.capitalize()))

    index.g.parent_page = index.g.url('')
    index.g.parent_page_link_name = "^ Up to API Documentation"  

    return index.render_template('api_v1/docs_post_{}.html'.format(object_type)) 


@apiv1.route('/api/v1/class/')
def get_class():

    # Read GET arguments
    load_records = request.args.get('load_records')
        
    # Compile list of classes
    classes = backend.get_all_record_classes()
    output = [rc.definition() for rc in classes]

    # Output
    return jsonify(output)

@apiv1.route('/api/v1/class/<class_handle_or_id>/')
def get_record(class_handle_or_id):
    if class_handle_or_id.isdigit():
        class_id = class_handle_or_id
    else:
        class_id = backend.get_record_class_id(class_handle_or_id)

    # Read GET arguments
    load_records = request.args.get('load_records')
        

    # Get record class
    rc = backend.get_record_class(class_id)

    return jsonify({'class' : rc.definition(load_records)})

@apiv1.route('/api/v1/record/')
def get_records():
    
    """
    Get's all records. GET parameters can be entered as filters.
    - class: return only records of given class. /api/v1/record/?class=computer
    """
    # GET
    class_handle_or_id = request.args.get('class')

    if class_handle_or_id.isdigit():
        class_id = class_handle_or_id
    else:
        class_id = backend.get_record_class_id(class_handle_or_id)    

    # Get records
    if class_id:
        rc = backend.get_record_class(class_id)
        records = rc.records()
    else:
        records = backend.get_all_records()
        records.sort(key=lambda x: x.record_class.name)

    # Compile output list
    output = []
    for r in records:
        output.append(r.definition())

    return jsonify({'records' : output})

 

@apiv1.route('/api/v1/record/<record_handle_or_id>', methods=['GET'])
@apiv1.route('/api/v1/record/<record_handle_or_id>/', methods=['GET'])
def route_record_handle(record_handle_or_id):
    if record_handle_or_id.isdigit():
        rec_id = record_handle_or_id
    else:
        rec_id = index.backend.get_record_id(class_handle, record_handle_or_id)

    record = backend.get_record(rec_id)
    return jsonify({'record' : record.definition()})