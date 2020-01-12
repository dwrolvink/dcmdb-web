""" Blueprint module to serve /api/v1/ routes """
from .integrator import Integrator
index = Integrator() 

# Initialize Blueprint
api = index.Blueprint('api/v1', __name__)

# -- Routes
@api.route('/ui/api/v1/object')
def render_object_types():
    # Set the global title variable
    index.g.title = 'All object types'

    index.g.objects = index.backend.get_all_object_types()

    return index.render_template('api_v1_object_home.html') 

@api.route('/ui/api/v1/object/<object_type_handle>')
def render_object_list(object_type_handle):
    # Set the global title variable
    index.g.title = 'All objects of type '+object_type_handle
    index.g.parent_page = "/ui/api/v1/object"
    index.g.parent_page_link_name = "^ Up to all objects"

    # Set all objects listed in this page
    index.g.objects = index.backend.get_all_objects_of_type(object_type_handle)
    
    # Create new object form
    from .forms import CreateObjectForm
    form = CreateObjectForm()    

    return index.render_template('api_v1_object_list.html', form=form)     

@api.route('/ui/api/v1/object/<object_type_handle>/<obj_handle>')
def render_object_details(object_type_handle, obj_handle):

    # Set object
    obj = index.backend.get_object_instance(object_type_handle, obj_handle)
    index.g.obj = obj

    # Get properties
    index.g.properties = obj.get_all_properties()

    # Set page constants
    index.g.title = obj.value
    index.g.parent_page = "/ui/api/v1/object/"+object_type_handle
    index.g.parent_page_link_name = "^ Up to "+object_type_handle

    return index.render_template('api_v1_object_details.html') 

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
