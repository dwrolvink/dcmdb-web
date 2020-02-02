""" Blueprint module to serve /ui/ routes """
from ..integrator import Integrator
index = Integrator() 
backend = index.backend

from flask import request, redirect, url_for, jsonify



"""
            INIT
"""


# Initialize Blueprint
ui = index.Blueprint('ui', __name__)

# -- Helper functions
def get_record_class(rc_handle):
    rc_id = index.backend.get_record_class_id(rc_handle)
    return index.backend.get_record_class(rc_id)

def get_record(rc_handle, record_handle):
    rec_id = index.backend.get_record_id(rc_handle, record_handle)
    return index.backend.get_record(rec_id)

# Globals
def url(url):
    return '/ui/' + url

def api_url(url):
    return '/api/v1/' + url

def init_globals(g, title):
    g.title = title
    g.url = url
    g.api_url = api_url




"""
            VIEWS
"""

@ui.route('/ui')
@ui.route('/ui/')
def render_homepage():
    init_globals(index.g, 'Root')
    return index.render_template('ui/home.html') 


@ui.route('/ui/class')
@ui.route('/ui/class/')
def render_class_list():
    init_globals(index.g, 'All Record Classes')

  
    classes = index.backend.get_all_record_classes()
    classes.sort(key=lambda x: x.name)

    # only_object_types = []
    # for rc in classes:
    #     if rc.type == 'object':
    #         only_object_types.append(rc)
    index.g.objects = classes

    # Create new record form
    from ..forms import CreateRecordClassForm
    form = CreateRecordClassForm()    

    r = form.validate_on_submit()    

    return index.render_template('ui/class_list.html', form=form) 

@ui.route('/ui/class/<class_handle>')
@ui.route('/ui/class/<class_handle>/')
def render_class_details(class_handle):
    init_globals(index.g, ('All records of class '+ class_handle))

    # Set navigation link
    index.g.parent_page = "/ui/class"
    index.g.parent_page_link_name = "^ Up to all classes"
    
    # Get record class
    rc = get_record_class(class_handle)
    index.g.rc = rc

    # Set all records listed in this page
    index.g.records = rc.records()

    # Get all "applies_to"
    applies_to = []
    for t in rc.applies_to:
        applies_to.append(get_record_class(t))
    index.g.applies_to = applies_to

    # Get all "accepts"
    accepts = []
    for t in rc.accepts:
        accepts.append(get_record_class(t))
    index.g.accepts = accepts
    
    # Create new record form
    from ..forms import CreateRecordForm
    form = CreateRecordForm()    

    r = form.validate_on_submit()

    return index.render_template('ui/class_details.html', form=form)  

@ui.route('/ui/class/<class_handle>/<record_handle_or_id>', methods=['GET'])
@ui.route('/ui/class/<class_handle>/<record_handle_or_id>/', methods=['GET'])
def route_record_details(class_handle, record_handle_or_id):
    rec_id = to_record_id(class_handle, record_handle_or_id)

    # Get record 
    record = index.backend.get_record(rec_id)
    index.g.record = record

    init_globals(index.g, title=record.label)

    # Get class
    rc = record.record_class

    # Set index
    index.g.title = record.label 
    index.g.rc = rc
    index.g.parent_page = "/ui/class/"+record.class_handle
    index.g.parent_page_link_name = "^ Up to "+record.class_handle         

    # Init forms
    from ..forms import TestForm
    form = TestForm()

    # Set the rc_handle select field's choices    
    form.sel_class_handle.choices = get_class_select_list(rc)  

    # Set alias_class_handle choices to empty, so we don't get an error
    form.sel_alias_class_handle.choices = [(0, "")]    

    return index.render_template('ui/record_details.html', form=form)




"""
            MUTATIONS - CREATE
"""


@ui.route('/ui/class', methods=['POST'])
@ui.route('/ui/class/', methods=['POST'])
def create_new_class():
    # Init form
    from ..forms import CreateRecordClassForm
    form = CreateRecordClassForm()

    if form.validate_on_submit():
        rc = index.backend.RecordClassDefinition(index.backend)
        rc.handle = form.class_handle.data
        rc.type = 'object'
        rc.name = form.class_name.data
        rc.description = form.class_description
        rc.create()

    return render_class_list()

@ui.route('/ui/class/<class_handle>', methods=['POST'])
@ui.route('/ui/class/<class_handle>/', methods=['POST'])
def create_new_record(class_handle):
    # Init form
    from ..forms import CreateRecordForm
    form = CreateRecordForm()

    rc_id = backend.get_record_class_id(class_handle)
    rc = backend.get_record_class(rc_id)

    if form.validate_on_submit():
        rd = index.backend.RecordDefinition(index.backend)
        rd.handle = form.record_handle.data
        rd.class_handle = class_handle
        if rc.type == "value":
            rd.value = form.record_value.data
        else:
            rd.label = form.record_value.data

        rd.create()

    return render_class_details(class_handle)


@ui.route('/ui/class/<class_handle>/<record_handle_or_id>', methods=['POST'])
@ui.route('/ui/class/<class_handle>/<record_handle_or_id>/', methods=['POST'])
def route_record_add_property(class_handle, record_handle_or_id):
    rec_id = to_record_id(class_handle, record_handle_or_id)

    # Get record 
    record = index.backend.get_record(rec_id)
    index.g.record = record

    # Get class
    rc = record.record_class    

    # Init forms
    from ..forms import TestForm
    form = TestForm()    

    # Set the rc_handle select field's choices    
    form.sel_class_handle.choices = get_class_select_list(rc) 

    # Collect input
    # ------------------------------------------------------------------
    # class handle
    input_class_handle = form.sel_class_handle.data 

    # Alias class id
    input_alias_class_id = form.sel_alias_class_handle.data 

    # record id
    if form.sel_record_handle.data:
        input_record_id = form.sel_record_handle.data.split('; ')[1]

    # alias record id
    if form.sel_alias_record_handle.data:
        input_alias_record_id = form.sel_alias_record_handle.data.split('; ')[1]

    # value
    input_value = form.value.data

    # Get record class
    input_rc_id = backend.get_record_class_id(input_class_handle)
    input_rc = backend.get_record_class(input_rc_id)   

    # Process input
    # ------------------------------------------------------------------
    if input_rc.type == "value":
        record.add_valued_property(input_class_handle, input_value)

    elif input_rc.type == "object":
        print("---" + str(input_record_id))
        record.add_property(input_record_id)

    elif input_rc.type == "linked-object":
        # Create new linked-object
        rdef = backend.RecordDefinition(backend)
        rdef.class_handle = input_class_handle
        rdef.target_id = record.id
        rdef.label = input_rc.name
        rdef.create()

    elif input_rc.type == "alias":
        # Create new alias record
        rdef = backend.RecordDefinition(backend)
        rdef.class_handle = input_class_handle # the alias
        rdef.alias_dst_id = record.id          # current record
        rdef.alias_src_id = input_alias_record_id  # the selected record to be aliased
        rdef.create()

    # Call main function
    return redirect(request.path, code=302)




"""
            HELPER-FUNCTIONS
"""


def get_class_select_list(record_class):
    """
    From the list of all classes, it tests which should be shown to objects of 
    the given class. It then compiles a list of classes in the form of [(rc.handle, rc)]
    so that it is understood by the Flask-WTF Select input.
    """
    rc = record_class
    classes = index.backend.get_all_record_classes()
    class_choice_list = [(0, ' ')]

    for t in classes:  

        if rc.handle in t.applies_to:
            append = True
        elif t.applies_to == []:
            if rc.accepts == []:
                append = True
            elif t.handle in rc.accepts:
                append = True
            else:
                append = False
        else:
            append = False

        if append:        
            class_choice_list.append((t.handle, t.name))  

    return class_choice_list

def get_record_select_list(chosen_rc_handle):
    records = backend.get_records(chosen_rc_handle)
    choice_list = []
    for r in records:
        choice_list.append((r.id, r))

    return choice_list

def to_record_id(class_handle, record_handle_or_id):
    if record_handle_or_id.isdigit():
        rec_id = record_handle_or_id
    else:
        rec_id = index.backend.get_record_id(class_handle, record_handle_or_id)  

    return rec_id  

