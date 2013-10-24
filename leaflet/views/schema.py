import colander
import deform

from trumpet.resources import MemoryTmpStore

tmpstore = MemoryTmpStore()

def deferred_choices(node, kw):
    choices = kw['choices']
    return deform.widget.SelectWidget(values=choices)

def make_select_widget(choices):
    return deform.widget.SelectWidget(values=choices)


class AddUserSchema(colander.Schema):
    user = colander.SchemaNode(
        colander.Integer(),
        title="User",
        widget=deferred_choices,
        description="User to add",
        )
    
    
#############################
# event schemas
#############################

class PlanEventSchema(colander.Schema):
    venue = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_choices,
        title='Venue',
        )
    event_type = colander.SchemaNode(
        colander.Integer(),
        title='Event Type',
        widget=deferred_choices,
        )
    title = colander.SchemaNode(
        colander.String(),
        title='Event Title',
        )
    start = colander.SchemaNode(
        colander.DateTime(),
        title='Start Date/Time',
        widget=deform.widget.DateTimeInputWidget()
        )
    end = colander.SchemaNode(
        colander.DateTime(),
        title='End Date/Time',
        widget=deform.widget.DateTimeInputWidget()
        )
    description = colander.SchemaNode(
        colander.String(),
        title='Event Description',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60)
        )


#############################
# venue schemas
#############################

class AddressSchema(colander.MappingSchema):
    street = colander.SchemaNode(
        colander.String(),
        title='Street',
        )
    city = colander.SchemaNode(
        colander.String(),
        title='City',
        missing='',
        )
    state = colander.SchemaNode(
        colander.String(),
        title='State',
        missing='',
        )
    zip = colander.SchemaNode(
        colander.String(),
        title='Zip Code',
        missing='',
        )


class AddVenueSchema(colander.Schema):
    venue = colander.SchemaNode(
        colander.String(),
        title='Venue Name',
        )
    description = colander.SchemaNode(
        colander.String(),
        title='Description',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )
    
class OldAddVenueSchema(colander.Schema):
    host = colander.SchemaNode(
        colander.String(),
        title='Venue Host',
        widget=deferred_choices,
        )
    venue = colander.SchemaNode(
        colander.String(),
        title='Venue Name',
        )
    audience = colander.SchemaNode(
        colander.Integer(),
        title='Audience',
        widget=deferred_choices,
        )
    address = AddressSchema()
    image = colander.SchemaNode(
        deform.FileData(),
        widget=deform.widget.FileUploadWidget(tmpstore),
        )
    description = colander.SchemaNode(
        colander.String(),
        title='Description',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )
        

class OldEditVenueSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Venue Name',
        )
    address = AddressSchema()
    image = colander.SchemaNode(
        deform.FileData(),
        missing='',
        widget=deform.widget.FileUploadWidget(tmpstore),
        )
    description = colander.SchemaNode(
        colander.String(),
        title='Description',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )
        
