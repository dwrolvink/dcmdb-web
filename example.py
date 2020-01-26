from importlib import reload
from backend.app import App

app = App()

# Get record
rec = app.get_record(14)

# # Get list of properties (in object form)
# rec.table
# rec.table.print() 

# Get list of members (in object form)
rec.member_table
rec.member_table.print()

# # Get list of properties (in list form)
# print(rec.list)

# Get list of members (in list form)
print(rec.member_list)

# Print table of properties in terminal
#rec.table.print()

# Get data from a property
#print(rec.table.id)

# # Use list to be able to loop over properties
# for p in rec.list:
#     print(p[0] + ": " + str(p[1]))

# # Same as list, but only custom attributes
# for p in rec.custom_attributes:
#     print(p[0] + ": " + str(p[1]))

rec.member_list[0][1][0].print()


