""" Blueprint module to serve /api/v1/ routes """
from .integrator import Integrator
index = Integrator() 

from flask import request, redirect, url_for

# Initialize Blueprint
api = index.Blueprint('api/v1', __name__)

# -- Routes
@api.route('/ui/api/v1/object')
def render_object_types():
    # Set the global title variable
    index.g.title = 'All object types'

    index.g.objects = index.backend.get_all_object_types()

    # Create new object form
    from .forms import CreateObjectTypeForm
    form = CreateObjectTypeForm()    

    r = form.validate_on_submit()    

    return index.render_template('api_v1_object_home.html', form=form) 

@api.route('/ui/api/v1/object', methods=['POST'])
def create_new_object_type():
    # Init form
    from .forms import CreateObjectTypeForm
    form = CreateObjectTypeForm()

    if form.validate_on_submit():
        ot_handle = form.object_type_handle.data
        ot_name = form.object_type_name.data
        ot_description = form.object_type_description
        r = index.backend.create_object_type(ot_handle, ot_name, ot_description)

    return render_object_types()




@api.route('/ui/api/v1/object/<object_type_handle>')
def render_object_list(object_type_handle):
    # Set the global title variable
    index.g.title = 'All objects of type '+object_type_handle
    index.g.parent_page = "/ui/api/v1/object"
    index.g.parent_page_link_name = "^ Up to all objects"
    

    # Set all objects listed in this page
    index.g.objects = index.backend.get_all_objects_of_type(object_type_handle)

    ot = index.backend.get_object_type_by_handle(object_type_handle)
    index.g.object_type_name = ot.name
    
    # Create new object form
    from .forms import CreateObjectForm
    form = CreateObjectForm()    

    r = form.validate_on_submit()

    return index.render_template('api_v1_object_list.html', form=form)  

@api.route('/ui/api/v1/object/<object_type_handle>', methods=['POST'])
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
def render_object_details(object_type_handle, obj_handle):

    # Get object (on basis of the url)
    object = index.backend.get_object_instance(object_type_handle, obj_handle)
    index.g.title = object.value  

    # PROCESS INPUT
    # -----------------------------------------------------------------

    # Create add properties form
    # These are split in two: first the object type is chosen, then the
    # object itself. This allows us to first get all the object types, 
    # and then in the next step get all the objects of that type. 
    # This allows us to not have to get ALL the objects in the database
    # when this page is loaded.

    # Init forms
    from .forms import AddPropertyForm1, AddPropertyForm2
    form1 = AddPropertyForm1()
    form2 = AddPropertyForm2()

    # Unless set differently later on, load form1
    form = form1

    # Also tell the template which form to load
    # Start with form1
    index.g.form = "form1"

    # Fill form1 with a tuple list of all object types
    # [(ot.handle, ot.name)] <- ot.handle will appear in form.field.data
    ots = index.backend.get_all_object_types()
    ot_choices = []
    for ot in ots:  # compile tuple list
        ot_choices.append((ot.handle, ot.name))  
    # Set the ot_handle select field's choices    
    form1.object_type_handle.choices = ot_choices    

    # Get submitted ot_handle
    # When form2 is loaded, it will be still in form1
    # When form2 is submitted, the value will be in form2
    if form2.object_type_handle.data:
        ot_handle = form2.object_type_handle.data
    elif form1.object_type_handle.data:
        ot_handle = form1.object_type_handle.data

    # Fill form2
    # get all objects of the submitted type
    objs = index.backend.get_all_objects_of_type(ot_handle)
    obj_choices = []
    i = 0
    for o in objs:
        obj_choices.append((o.handle, o.value))
        i += 1   
    # Set the object select field's choices      
    form2.object_instance_handle.choices = obj_choices

    # First form has been posted, fill in second form
    if form1.submit1.data and form1.validate_on_submit():
        # fill in the object_type, which was collected in form1
        ot_handle = form1.object_type_handle.data
        form2.object_type_handle.data = ot_handle
        #form2.object_type_handle.render_kw = {'disabled': 'disabled'}
        
        index.g.form = "form2"
        form = form2

    # Second form has been posted, execute
    if form2.submit2.data and form2.validate_on_submit():
        # Combine ot_handle and object_handle to the property_url
        property_url = (form2.object_type_handle.data + "/" + 
                       form2.object_instance_handle.data)

        # add property
        index.backend.add_property(property_url, object.url)

    # END PROCESS INPUT -----------------------------------------------

    # Get object again, as the properties may have changed during the 
    # execution of this function
    object = index.backend.get_object_instance(object_type_handle, obj_handle)
    index.g.obj = object

    # Get properties
    index.g.properties = object.get_all_properties()

    # Set page constants
    index.g.parent_page = "/ui/api/v1/object/"+object_type_handle
    index.g.parent_page_link_name = "^ Up to "+object_type_handle      

    return index.render_template('api_v1_object_details.html', form=form)


     


