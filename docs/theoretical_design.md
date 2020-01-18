# Different types of objects
To create a new object, we first need to create an **object type**, or named **types** in short.

There are three types at the time of writing: free objects, linked-objects, and UserDefinedValues.

Let's take the example of the following ideas: a car, it's insurance, and monthly costs associated with the insurance.

A car is a **free object**. It can be made a member of a group of cars, it can be added to a department, a location, etc. 
In this case, the department would be the **property** of the car. The car is then at the same time a **member** of the 
department.

A car insurance is a different case. You can have the insurance type be global, but any actual car insurance will allways apply
to a car, and one car only. (At least in the case of private insurances). In our lingo, a car insurance is thus a **linked-object**,
it can only have one member: a certain car. It can have any number of properties though. 

Cost monthly is a basic value. We don't want to create a new object for every cost listed. Each object has values a name and 
handle value. Cost monthly would be a user defined value, or **UDV**. An object can have any kind of UDV's, even multiple of 
the same kind. (Though that would be a bit weird in this case, imagine a UDV called incidental_cost.) Since a UDV is a value,
it can't have any properties. A UDV can only have one member, though the UDV-type will list any object that has a UDV with its
type as a member. So for a UDV type of "telephone_number", if you go to that type, you'll find all objects that 
have a phone number associated with them.

