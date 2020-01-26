""" Blueprint module to serve /api/v1/ routes """
from .integrator import Integrator
index = Integrator() 

from flask import request, redirect, url_for

# Initialize Blueprint
api = index.Blueprint('api/v1', __name__)

# -- Helper functions
def get_record_class(rc_handle):
    rc_id = index.backend.get_record_class_id(rc_handle)
    return index.backend.get_record_class(rc_id)

def get_record(rc_handle, record_handle):
    rc_id = index.backend.get_record_class_id(rc_handle)
    rec_id = index.backend.get_record_id(rc_id, record_handle)
    return index.backend.get_record(rec_id)


# -- Routes
@api.route('/ui/api/v1')
@api.route('/ui/api/v1/')
def render_homepage():
    index.g.title = 'Root'
    return index.render_template('api_v1_home.html') 

@api.route('/ui/api/v1/value_type')
@api.route('/ui/api/v1/value_type/')
def render_value_types():
    index.g.title = 'All Simple Value Types'

    types = index.backend.get_all_types()
    only_value_types = []
    for t in types:
        if t.data_type == 'value':
            only_value_types.append(t)
    index.g.records = only_value_types

    # Create new record form
    from .forms import CreateValueTypeForm
    form = CreateValueTypeForm()    

    r = form.validate_on_submit()    

    return index.render_template('api_v1_value_class_list.html', form=form)     

@api.route('/ui/api/v1/value_type', methods=['POST'])
@api.route('/ui/api/v1/value_type/', methods=['POST'])
def create_new_value_type():
    # Init form
    from .forms import CreateValueTypeForm
    form = CreateValueTypeForm()

    if form.validate_on_submit():
        t_handle = form.class_handle.data
        t_data_type = 'value'
        t_unit = form.class_unit.data
        t_name = form.class_name.data
        t_description = form.class_description
        r = index.backend.udv.new(t_handle, 
                                      t_name, 
                                      t_description, 
                                      data_type=t_data_type,
                                      unit=t_unit)

    return render_value_types()

@api.route('/ui/api/v1/value_type/<class_handle>')
@api.route('/ui/api/v1/value_type/<class_handle>/')
def render_value_class_details(class_handle):
    index.g.title = class_handle

    class_obj = index.backend.get_class_by_handle(class_handle)
    index.g.class_obj = class_obj

    # Get all records that have this UDV set
    index.g.records = index.backend.udv.get_set_udv_values(class_handle)

    return index.render_template('api_v1_value_class_details.html')  

@api.route('/ui/api/v1/class')
@api.route('/ui/api/v1/class/')
def render_class_list():
    # Set the global title variable
    index.g.title = 'All Record Classes'

    classes = index.backend.get_all_record_classes()
    classes.sort(key=lambda x: x.name)

    # only_object_types = []
    # for rc in classes:
    #     if rc.type == 'object':
    #         only_object_types.append(rc)
    index.g.objects = classes

    # Create new record form
    from .forms import CreateRecordClassForm
    form = CreateRecordClassForm()    

    r = form.validate_on_submit()    

    return index.render_template('api_v1_class_list.html', form=form) 

@api.route('/ui/api/v1/class', methods=['POST'])
@api.route('/ui/api/v1/class/', methods=['POST'])
def create_new_class():
    # Init form
    from .forms import CreateRecordClassForm
    form = CreateRecordClassForm()

    if form.validate_on_submit():
        rc = index.backend.RecordClassDefinition(index.backend)
        rc.handle = form.class_handle.data
        rc.type = 'object'
        rc.name = form.class_name.data
        rc.description = form.class_description
        rc.create()

    return render_class_list()




@api.route('/ui/api/v1/class/<class_handle>')
@api.route('/ui/api/v1/class/<class_handle>/')
def render_class_details(class_handle):
    # Set the global title variable
    index.g.title = 'All records of class '+ class_handle
    index.g.parent_page = "/ui/api/v1/class"
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
        accepts.append(get_record_class(class_handle))
    index.g.accepts = accepts
    
    # Create new record form
    from .forms import CreateRecordForm
    form = CreateRecordForm()    

    r = form.validate_on_submit()

    return index.render_template('api_v1_class_details.html', form=form)  

@api.route('/ui/api/v1/class/<class_handle>', methods=['POST'])
@api.route('/ui/api/v1/class/<class_handle>/', methods=['POST'])
def create_new_record(class_handle):
    # Init form
    from .forms import CreateRecordForm
    form = CreateRecordForm()

    if form.validate_on_submit():
        rd = index.backend.RecordDefinition(index.backend)
        rd.handle = form.record_handle.data
        rd.class_handle = class_handle
        rd.value = form.record_value.data
        rd.create()

    return render_class_details(class_handle)




@api.route('/ui/api/v1/class/<class_handle>/<record_handle>', methods=['GET', 'POST'])
@api.route('/ui/api/v1/class/<class_handle>/<record_handle>/', methods=['GET', 'POST'])
def route_record_handle(class_handle, record_handle):
    # Get record id
    rc = get_record_class(class_handle)
    rec_id = index.backend.get_record_id(rc.id, record_handle)

    # Call main function
    return render_record_details(rec_id)

@api.route('/ui/api/v1/class/<class_handle>/<record_handle>/<lo_class_handle>/<lo_id>', methods=['GET', 'POST'])
@api.route('/ui/api/v1/class/<class_handle>/<record_handle>/<lo_class_handle>/<lo_id>/', methods=['GET', 'POST'])
def route_linked_object_handle(class_handle, record_handle, lo_class_handle, lo_id):
    # Call main function
    return render_record_details(lo_id)    

def render_record_details(record_id):
    """
    The first part of this function deals with handling the input.
    There are three forms: the first asks the user to fill in a type that
    they want to add. If this type is a value type, and unit is not 'object' form3 will be shown.
    Otherwise, form2 will be shown.
    """

    # Get record 
    record = index.backend.get_record(record_id)
    index.g.record = record

    # Get class
    rc = record.record_class

    # Set title
    index.g.title = record.label 



    # PROCESS INPUT
    # -----------------------------------------------------------------

    # Init forms
    from .forms import AddPropertyForm_choose_class
    from .forms import AddPropertyForm_choose_record
    from .forms import AddPropertyForm_choose_value

    choose_class  = AddPropertyForm_choose_class()
    choose_record = AddPropertyForm_choose_record()
    choose_value  = AddPropertyForm_choose_value()

    # Unless set differently later on, load form1
    form = choose_class

    # Also tell the template which form to load
    # Start with form1
    index.g.form = "choose_class"

    #  --- Step 1: load form1

    # Fill form1 with a tuple list of all classes
    # [(rc.handle, rc.name)] <- rc.handle will appear in form.field.data
    classes = index.backend.get_all_record_classes()
    class_choice_list = []
    for t in classes:  # compile tuple list

        # Show object?
        # - t.applies_to_all == True --> yes
        # - rc.handle in t.applies_to --> yes
        # - t.handle not in rc.accepts (when accepts is set) --> no
        # - --> yes
        if t.applies_to_all:
            append = True
        elif rc.handle in t.applies_to:
            append = True
        elif t.applies_to == []:
            # Applies to not set, see if rc accepts the property
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

    # Set the rc_handle select field's choices    
    choose_class.class_handle.choices = class_choice_list    

    # --- Step 2: process form1

    # First form has been posted, fill in second|third form
    if choose_class.submit1.data and choose_class.validate_on_submit():
        # Get type
        class_handle = choose_class.class_handle.data
        class_obj = get_record_class(class_handle)

        # Find out which form to load
        if class_obj.type == 'value':
            index.g.form = "choose_value"
            form = choose_value
            choose_class.class_handle.data = class_obj.handle

        elif class_obj.type == 'object':
            index.g.form = "choose_record"
            form = choose_record
            choose_record.class_handle.data = class_obj.handle

            records = class_obj.records()
            choices = []
            for r in records:
                choices.append((str(r.id), r.label))      
            choose_record.record_handle.choices = choices 

        elif class_obj.type in ['linked-object','alias']:
            index.g.form = "choose_record"
            form = choose_record
            choose_record.class_handle.data = class_obj.handle

            choices = []
            for subclass in class_obj.accepts:
                subclass_obj = get_record_class(subclass)
                if subclass_obj:
                    records = subclass_obj.records()
                    for r in records:
                        choices.append((str(r.id), r.label))      
            
            choose_record.record_handle.choices = choices             

    # Second form has been posted, execute
    if choose_record.submit2.data:
        # Get data
        class_handle = choose_record.class_handle.data
        record_id = choose_record.record_handle.data
        class_obj = get_record_class(class_handle)

        # Fill in form2, otherwise we can't validate correctly
        if class_obj.type == "object":
            records = class_obj.records()
            choices = []
            for r in records:
                choices.append((str(r.id), r.label))      
            choose_record.record_handle.choices = choices 

        elif class_obj.type in ['linked-object', 'alias']:
            index.g.form = "choose_record"
            form = choose_record
            choose_record.class_handle.data = class_obj.handle

            choices = []
            for subclass in class_obj.accepts:
                subclass_obj = get_record_class(subclass)
                if subclass_obj:
                    records = subclass_obj.records()
                    for r in records:
                        choices.append((str(r.id), r.label))      
            
            choose_record.record_handle.choices = choices 

        if choose_record.validate_on_submit():
            if class_obj.type == "object":
                # Add given record as property to current record
                index.g.record.add_property(record_id)

            elif class_obj.type in ['linked-object']:
                # create linked-object
                lo = index.backend.RecordDefinition(index.backend)
                lo.class_handle = class_handle
                lo.append_to_id = index.g.record.id
                lo.create()

                # add given record as property to linked object
                lo_obj = index.backend.get_record(lo.id)
                lo_obj.add_property(record_id)

            elif class_obj.type in ['alias']:
                # create alias
                alias = index.backend.RecordDefinition(index.backend)

                alias.class_handle = class_handle
                alias.alias_dst_id = index.g.record.id

                # add given record as property to linked object
                alias.alias_src_id = record_id

                alias.create()


    elif choose_value.submit3.data:
        if choose_value.validate_on_submit():
            class_handle = choose_value.class_handle.data
            value = choose_value.value.data 
            index.g.record.add_valued_property(class_handle, value)
     

    # END PROCESS INPUT -----------------------------------------------

    # Get object again, as the properties may have changed during the 
    # execution of this function
    index.g.record = index.backend.get_record(index.g.record.id)

    # Set page constants
    index.g.parent_page = "/ui/api/v1/class/"+index.g.record.class_handle
    index.g.parent_page_link_name = "^ Up to "+index.g.record.class_handle      

    return index.render_template('api_v1_record_details.html', form=form)





