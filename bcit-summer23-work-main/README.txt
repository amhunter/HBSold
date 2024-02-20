TRUST BASED REVISION APPLICATION
2023 ALBERTO IGLESIAS & AARON HUNTER

This is an application which allows for the input of propositional formulas
to create states, as well as calculating a revision operation on a series of
states.

Contents:
- How to run the interface
- How to use the interface
- How the trust calculations are implemented
- How to create testcase files
- Note to future developers


--- HOW TO RUN THE INTERFACE

Download Python from its website, ensuring it is a version compatible with 
your system. Download the contents of this repository and ensure the folder 
structure does not change. Double-click the "interface.py" file to 
run the application.


--- HOW TO USE THE INTERFACE

When opening the application, the panel on the left is initially set to the
"Formula entry" tab. This screen can be used to enter formulas, which will be
converted into states. Propositional variables are entered with the middle
entry box, and operators with the buttons beneath.

Once an initial state is created, new formulas created will by default add to
the initial state. By switching the type of formula at the bottom of the screen
to "Observation" or "Agent", new states can be added.

Observation states will always be trusted as part of the revision process. If
a formula is entered with an agent, the agent will have its trust tracked in
the "Agent trust entry" tab of the left panel. The interactions of trust are
discussed in the section below.

Once you have a set of states, clicking "Calculate output" will create a new
"Output" state with the final result of the calculation.

The "File" menu allows for a set of states to be loaded from a file, which
can make repeated tests easier to perform. To see how to make your own state
files, see the section below titled "How to create testcase files".

The "Edit" menu allows for switching between the default Hamming distance for
calculating the distance between states to the Weighted Hamming distance, which
can change how states are evaluated. Once set, the values of propositional
variables can be set through the "Parameter weight entry" tab of the left panel.

Another option on the "Edit" menu is to "Change trust and threshold values".
This option opens a new panel where parameters that affect the way trust is
evaluated can be changed. Explanations for these variables are shown on the
menu, and more information on the trust calculations is included in the
"How the trust calculations are implemented" section below.

The "View" menu allows the toggling of a simplified view, which omits the list
of states for states with an associated formula. This can make large state lists
take up less screen space.


--- HOW THE TRUST CALCULATIONS ARE IMPLEMENTED

Trust per agents is adjusted based on several factors, and this behaviour can
be modified from the "Edit > Change trust and threshold values" menu.

There are 6 values which can be modified in this menu:

- Trust Observation Decrease
- Trust Observation Increase
- Trust Decrease
- Trust Increase
- No Trust Threshold
- Difference Threshold

These values factor into the trust revision calculation in the following ways:

If there are any observations in the input states, the observed states will be
compared against the information from each agent. 
If an agent disagrees with an observation, their information will not be revised
by and their trust will be decreased according to the 
"Trust Observation Decrease" value.
If the agent's information agrees with the observation, its trust will be 
increased by the "Trust Observation Increase" value.

After this, the remaining agents are compared against each other. If two agents
disagree completely, and their trust difference is greater than the "Difference
Threshold" value, the less trusted agent will not be counted in the revision
process, and its trust will be decreased by the "Trust Decrease" value.
If the agents agree to an extent and their trust is greater than the
"Difference Threshold" value, the less trusted agent will have its trust
increased by the "Trust Increase" value.

After these calculations, if any agent's trust falls below the "No Trust
Threshold", its information will not be revised by.

These values can be edited in the GUI. To change their default values, you can
open the "revision/revision.py" file and edit the values directly.


--- HOW TO CREATE TESTCASE FILES

The format of test files is as follows: (Issues in the formatting of the file
will probably cause errors)

Line 1: Initial formula(s), separated by / (slashes)

Formulas must be input with operators as the following characters:
NOT:		!
AND:		^
OR:		v
IMPLY:		>
IF AND ONLY IF:	=
Propositional variables must be one character only.

E.G.:
Av!B>C/A^B^C (A or NOT B implies C, A AND B AND C)

Line 2: Values of variables, separated by a , (comma)
Even if you intend to use regular hamming distance, weights for the variables
must be included, separated by commas. Ensure there are as many weights as there
are variables or you may get an error.

E.G.:
1,2,3 (A weight 1, B weight 2, C weight 3)

Line 3 and on: Name of an agent (if any), a : (colon), and a formula
If no name is specified, the formula will count as an observation.

E.G.:
bob:A^!B (Agent "bob" reports A AND NOT B)
:!Av!B (Observation: NOT A OR NOT B)


--- NOTE TO FUTURE DEVELOPERS

Information on the workings of the application are included in comments within
each source .py file.
