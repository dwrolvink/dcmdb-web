# Introduction
To create a new object, we first need to create an **object type**, or named **types** in short. If we want to create a computer and list the department it belongs to, we'd do this:

- create type "computer"
- create type "department"
- create object "server1" of type "computer"
- create object "HR" of type "department"
- set "department/hr" as a property of "computer/server1"  

A note on the nomenclature here: a parent object is called the property of the child object. A child object is called the 
member of the parent object. (This will make more sense later on).

There are three types at the time of writing: free objects, linked-objects, and UserDefinedValues.

# Different types of objects
Let's take the example of the following ideas: a car, it's insurance, and monthly costs associated with the insurance.

## Free objects
A car is a **free object**. It can be made a member of a group of cars, it can be added to a department, a location, etc. *(It can even be made a member of a computer, or coffee machine - even though that wouldn't make sense)*.
In this case, the department would be a **property** of the car. The car is then at the same time a **member** of the 
department.

A computer can have any member too. In this case it's hard to imagine a good case, but any case where you'd at a computer as a property: in that case that object will show up as a member of that computer.

## Linked-objects
A car insurance is a different case. Any car insurance will always apply to a car, and one car only. *(At least in the case of private insurances)*. In our lingo, a car insurance is thus a **linked-object**,
it can only have one member: a certain car. It can have any number of properties though. 

## UDVs
Cost monthly is a basic value. We don't want to create a new object for every cost listed, as this would muddy up our database pretty quickly.

Any object has two built-in values: a "value" (the name) and a "handle". Cost monthly would then be an extra value: a user defined value, or **UDV**. 

An object can have any kind of UDV's, even multiple of the same kind. *(Though that would be a bit weird in this case, imagine a UDV called incidental_cost).* Since a UDV is just a value, it can't have any properties. A UDV can only have one member, though the UDV-type will list any object that has a UDV with its type as a member. So for a UDV type of "telephone_number", if you go to that type, you'll find all objects that have a phone number associated with them.

