# Installation / Setup
None yet.

# Introduction
DCMDB is a simple tool to create objects and the relationships between them.
The main sellingpoint of dcmdb is that you can create any kind of object
and object-object relationship straight from the application.

Juggling dynamic relationships with performance is really hard (for me at least),
so don't expect good performance from this system when you have a massive amount
of objects.

# Data types
## Lists
Lists are stored in the Lists table. 
Each list has the following properties:
- id
- name
- type
- value

Type can be either enum, set, or range. 

**Enums** are simple comma separated lists of 
strings. 

**Sets** are lists of any combination of data types (i.e. string, 
List, Object). 

**Ranges** provide a way to define a multitude of values, without
listing them all. In the case of ints, a range might be x>0, x<=500. In the case
of strings, regex might be implemented.

The value property wil be parsed differently depending on the list type.
An enum of ('cow, horse', 'pig') will be encoded as 
```
cow\, horse, pig
```

A set can link to enums, objects, and other sets, but not to string values directly.
Any list in a set will be expanded so that its values are returned inline. 
Objects will not be expanded (as that wouldn't make sense).

For example:
```
list/1 type=enum value="a, b, c"
list/2 type=enum value="1, 2, 3"
list/3 type=set value="list/2, list/1"
list/4 type=set value="list/3"
```
Parsing the return value from list/4 will not return [list/2], [list/1], nor
will it return [1, 2, 3], [a, b, c]. Instead, it will return [1, 2, 3, a, b, c].

Thus, a set will function just like an enum (it returns a flat list), but there
is the added option to link to objects, and to compose composite lists from smaller
lists.

## Objects
Objects are the main star of the show. The lists are merely there in a supporting 
role. 

Objects are things like computers, departments. But also properties. For example
a computer object might be defined as:
```
name = serv-01
location = Amsterdam
department = Infrastructure
```
Name is often put in the "value" field of the object instance (more on that
later), location will be an object type, and "Amsterdam" will be an object 
instance of that type (location/Amsterdam).

This might seem needlessly complex, but in this way a location can have properties
of its own. Like location manager, helpdesk number, etc.

Thus, all the properties can be set through parent relationships.

There is one table with the object types, and another with the object 
instances. 

The object types have these properties:
- id
- name
- value_limit

Value_limit is a query that defines what kind of values
the value property can have (for any object instance of this type). Here,
we can say that the value has to be in an enum:

```
value_limit="in_list(1)"
```

Only use value_limits to set hard restriction. For example, it might be tempting
to create a locations enum, and then set that as the value_limit for the locations
object type. But such an action would not achieve anything, because the enum can
be freely appended at any time.

Note that if the list refered to in value_limit is an int_range, the value inserted 
will be explicitly converted to an int value.


The object instances have these properties:
- id
- type
- value
- properties
- members

Value is a string.  Properties is actually the parent-relationship 
column. It is renamed properties because any property will be created in 
dcmdb as a parent relationship. Members is the child_relationship. 

When a relationship is made, both the parent and the child are updated.

Example:
```
list/x type=enum name=dc_locations value="Amsterdam, New York"
objdef/x name="computer" 
```





:create enum

:create
obj computer
enum 
create obj location limit(enum )


