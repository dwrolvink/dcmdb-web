""" Blueprint module to serve /api/v1/ routes """
from .integrator import Integrator
index = Integrator() 

from flask import request, redirect, url_for

# Initialize Blueprint
api = index.Blueprint('api/v1', __name__)

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
    index.g.objects = only_value_types

    # Create new object form
    from .forms import CreateValueTypeForm
    form = CreateValueTypeForm()    

    r = form.validate_on_submit()    

    return index.render_template('api_v1_value_type_list.html', form=form)     

@api.route('/ui/api/v1/value_type', methods=['POST'])
@api.route('/ui/api/v1/value_type/', methods=['POST'])
def create_new_value_type():
    # Init form
    from .forms import CreateValueTypeForm
    form = CreateValueTypeForm()

    if form.validate_on_submit():
        t_handle = form.type_handle.data
        t_data_type = 'value'
        t_unit = form.type_unit.data
        t_name = form.type_name.data
        t_description = form.type_description
        r = index.backend.udv.new(t_handle, 
                                      t_name, 
                                      t_description, 
                                      data_type=t_data_type,
                                      unit=t_unit)

    return render_value_types()

@api.route('/ui/api/v1/value_type/<type_handle>')
@api.route('/ui/api/v1/value_type/<type_handle>/')
def render_value_type_details(type_handle):
    index.g.title = type_handle

    type_obj = index.backend.get_type_by_handle(type_handle)
    index.g.type_obj = type_obj

    # Get all objects that have this UDV set
    index.g.objects = index.backend.udv.get_set_udv_values(type_handle)

    return index.render_template('api_v1_value_type_details.html')  

@api.route('/ui/api/v1/object')
@api.route('/ui/api/v1/object/')
def render_object_types():
    # Set the global title variable
    index.g.title = 'All object types'

    types = index.backend.get_all_types()
    only_object_types = []
    for t in types:
        if t.data_type == 'object':
            only_object_types.append(t)
    index.g.objects = only_object_types

    # Create new object form
    from .forms import CreateObjectTypeForm
    form = CreateObjectTypeForm()    

    r = form.validate_on_submit()    

    return index.render_template('api_v1_type_list.html', form=form) 

@api.route('/ui/api/v1/object', methods=['POST'])
@api.route('/ui/api/v1/object/', methods=['POST'])
def create_new_object_type():
    # Init form
    from .forms import CreateObjectTypeForm
    form = CreateObjectTypeForm()

    if form.validate_on_submit():
        t_handle = form.type_handle.data
        t_data_type = 'object'
        t_name = form.type_name.data
        t_description = form.type_description
        r = index.backend.udv.new(t_handle, 
                                      t_name, 
                                      t_description, 
                                      data_type=t_data_type)

    return render_object_types()




@api.route('/ui/api/v1/object/<object_type_handle>')
@api.route('/ui/api/v1/object/<object_type_handle>/')
def render_object_list(object_type_handle):
    # Set the global title variable
    index.g.title = 'All objects of type '+object_type_handle
    index.g.parent_page = "/ui/api/v1/object"
    index.g.parent_page_link_name = "^ Up to all objects"
    

    # Set all objects listed in this page
    index.g.objects = index.backend.get_all_objects_of_type(object_type_handle)

    ot = index.backend.get_type_by_handle(object_type_handle)
    index.g.object_type_name = ot.name
    
    # Create new object form
    from .forms import CreateObjectForm
    form = CreateObjectForm()    

    r = form.validate_on_submit()

    return index.render_template('api_v1_object_list.html', form=form)  

@api.route('/ui/api/v1/object/<object_type_handle>', methods=['POST'])
@api.route('/ui/api/v1/object/<object_type_handle>/', methods=['POST'])
def create_new_object(object_type_handle):
    # Init form
    from .forms import CreateObjectForm
    form = CreateObjectForm()

    if form.validate_on_submit():
        obj_handle = form.object_handle.data
        value = form.object_value.data
        r = index.backend.create_object(object_type_handle, obj_handle, value)

    return render_object_list(object_type_handle)




@api.route('/ui/api/v1/object/<object_type_handle>/<obj_handle>', methods=['GET', 'POST'])
@api.route('/ui/api/v1/object/<object_type_handle>/<obj_handle>/', methods=['GET', 'POST'])
def render_object_details(object_type_handle, obj_handle):
    """
    The first part of this function deals with handling the input.
    There are three forms: the first asks the user to fill in a type that
    they want to add. If this type is a value type, form3 will be shown.
    Otherwise, form2 will be shown.
    """

    # Get object (on basis of the url)
    object = index.backend.get_object(object_type_handle, obj_handle)

    # Set title
    index.g.title = object.value  

    # PROCESS INPUT
    # -----------------------------------------------------------------

    # Init forms
    from .forms import AddPropertyForm_choose_type
    from .forms import AddPropertyForm_choose_object
    from .forms import AddPropertyForm_choose_value

    choose_type   = AddPropertyForm_choose_type()
    choose_object = AddPropertyForm_choose_object()
    choose_value  = AddPropertyForm_choose_value()

    # Unless set differently later on, load form1
    form = choose_type

    # Also tell the template which form to load
    # Start with form1
    index.g.form = "choose_type"

    #  --- Step 1: load form1

    # Fill form1 with a tuple list of all object types
    # [(ot.handle, ot.name)] <- ot.handle will appear in form.field.data
    types = index.backend.get_all_types()
    type_choices = []
    for t in types:  # compile tuple list
        type_choices.append((t.handle, t.name))  
    # Set the ot_handle select field's choices    
    choose_type.type_handle.choices = type_choices    

    # --- Step 2: process form1

    # First form has been posted, fill in second|third form
    if choose_type.submit1.data and choose_type.validate_on_submit():
        # Get type
        type_handle = choose_type.type_handle.data
        type_obj = index.backend.get_type_by_handle(type_handle)

        # Load correct form
        if type_obj.data_type == 'value':
            index.g.form = "choose_value"
            form = choose_value
            choose_type.type_handle.data = type_obj.handle

        elif type_obj.data_type == 'object':
            index.g.form = "choose_object"
            form = choose_object
            choose_object.type_handle.data = type_obj.handle

            objs = index.backend.get_all_objects_of_type(type_handle)
            choices = []
            for o in objs:
                choices.append((o.handle, o.value))      
            choose_object.object_handle.choices = choices

    # Second form has been posted, execute
    if choose_object.submit2.data:
        # Get data
        type_handle = choose_object.type_handle.data
        object_handle = choose_object.object_handle.data
        type_obj = index.backend.get_type_by_handle(type_handle)

        # Fill in form2, otherwise we can't validate correctly
        objs = index.backend.get_all_objects_of_type(type_handle)
        choices = []
        for o in objs:
            choices.append((o.handle, o.value))      
        choose_object.object_handle.choices = choices

        if choose_object.validate_on_submit():
            # Combine ot_handle and object_handle to the property_url
            property_url = (type_handle + "/" + object_handle)

            # add property
            index.backend.add_property(property_url, object.url)

    elif choose_value.submit3.data:
        if choose_value.validate_on_submit():
            type_handle = choose_value.type_handle.data
            value = choose_value.value.data 
            index.backend.udv.set_ud_value(object.url, type_handle, value)      

    # END PROCESS INPUT -----------------------------------------------

    # Get object again, as the properties may have changed during the 
    # execution of this function
    object = index.backend.get_object(object_type_handle, obj_handle)
    object.properties = object.get_properties()
    object.members = object.get_members()
    index.g.obj = object

    # Get members
    member_ids = object.get_members()
    members = []
    for mid in member_ids:
        members.append(index.backend.get_object_by_id(mid))
    index.g.members = members

    # Set page constants
    index.g.parent_page = "/ui/api/v1/object/"+object_type_handle
    index.g.parent_page_link_name = "^ Up to "+object_type_handle      

    return index.render_template('api_v1_object_details.html', form=form)





