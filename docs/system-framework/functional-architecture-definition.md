# Functional architecture definition

Functional architecture is the systematic examination of different implementation-independant architecture candidates to identify independent groups of [functions](../engineering-concepts/definitions.md) and their required ressources to be executed (so called [functional elements](../engineering-concepts/definitions.md)) from the [functional analysis](functional-analysis.md), to organize the way they exchange [data](../engineering-concepts/definitions.md) (so called [functional interfaces](../engineering-concepts/definitions.md)), and to select the best one according to the selected architecture criteria (Adapted from [REF\_3](../engineering-concepts/references.md))

## Functional interface creation

### Definition

JARVIS4SE allows to define a new functional interface named _\<functional interface name>_ through the following command:

```
<functional interface name> is a functional interface
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a functional interface named _\<functional interface name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <functional interface name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the functional interface.

{% hint style="info" %}
The first command is only required when the attribute does not exist.
{% endhint %}

## Functional element creation

### Definition

JARVIS4SE allows to define a new functional element named _\<functional element name>_ through the following command:

```
<functional element name> is a functional element
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a functional element named _\<functional element name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <functional element name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the functional element.

{% hint style="info" %}
The first command is only required when the attribute does not exist.
{% endhint %}

### Functional interface exposure

JARVIS4SE allows to indicate that a functional interface named _\<functional interface name>_ is exposed by a functional element named _\<functional element name>_ through the following command:

```
<functional element name> exposes <functional interface name>
```

### Context visualization

JARVIS4SE allows to visualize the context of a functional element named _\<functional element name>_ through the following command:

```
show context <functional element name>
```

Below an example of a context visualization for a functional element E which exposes an interface I with PlantUML:

```
E is a functional element
I is a functional interface
E exposes I
show context E
```

<figure><img src="../../.gitbook/assets/image (1) (1) (1).png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
The interface I is not shown until it allocated at least one data. Please refer to the chapter [#data-allocation](functional-architecture-definition.md#data-allocation "mention")
{% endhint %}

## Functional element decomposition

### Child definition

JARVIS4SE allows to decompose a functional element named _\<functional element name>_ into functional subelements named _\<functional subelement i name>_ through one of the following commands:

```
<functional element name> is composed of <functional subelement 1 name>, <functional subelement 2 name>
```

```
<functional subelement 1 name> composes <functional element name>
```

```
<functional subelement 1 name>, <functional subelement 2 name> compose <functional element name>
```

{% hint style="info" %}
The functional subelements must be created before as functional elements. Please refer to chapter [#functional-element-creation](functional-architecture-definition.md#functional-element-creation "mention")
{% endhint %}

### Decomposition visualization

JARVIS4SE allows to visualize the decomposition of a functional element named _\<functional element name>_ through the following command:

```
show decomposition <functional element name>
```

Below an example of a decomposition of the previous functional element E (which exposes I) into E1 (which exposes I and I1) and E2 (which exposes I1) with PlantUML:

```
E1 is a functional element
I1 is a functional interface
E1 exposes I
E1 exposes I1
E2 is a functional element
E2 exposes I1
E is composed of E1, E2
show decomposition E
```

<figure><img src="../../.gitbook/assets/image (1) (1) (1) (1).png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
The interfaces I and I1 are not shown until they allocated at least one data. Please refer to the chapter [#data-allocation](functional-architecture-definition.md#data-allocation "mention")
{% endhint %}

## Functional element state creation

### Definition

JARVIS4SE allows to define a new state named _\<state name>_ through the following command:

```
<state name> is a state
```

#### Entry state

JARVIS4SE allows to define a new entry state named _\<entry state name>_ through the following command:

```
<entry state name> is a <entry state type>
```

Where _\<entry state type>_ is an extension of the state concept defined in [Broken link](broken-reference "mention") which contains the keyword "entry".

#### Exit state

JARVIS4SE allows to define a new exit state named _\<exit state name>_ through the following command:

```
<exit state name> is a <exit state type>
```

Where _\<exit state type>_ is an extension of the state concept defined in [Broken link](broken-reference "mention") which contains the keyword "exit".

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a state named _\<state name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <state name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the functional element.

{% hint style="info" %}
The first command is only required when the attribute does not exist.
{% endhint %}

### Transition definition

#### Definition

JARVIS4SE allows to define a new state transition named _\<transition name>_ through the following command:

```
<transition name> is a transition
```

#### Source definition

JARVIS4SE allows to define the source of a transition named _\<transition name>_ as a state named <_state name_> through the following command:

```
The source of <transition name> is <state name>
```

{% hint style="danger" %}
The source of a transition is handled as an attribute of the transition named "source".

Therefore:

* Using this command multiple times for the same transition will only keep the latest state name.
* JARVIS4SE does not allow to define a new attribute named "source"
{% endhint %}

#### Destination definition

JARVIS4SE allows to define the destination of a transition named _\<transition name>_ as a state named <_state name_> through the following command:

```
The destination of <transition name> is <state name>
```

{% hint style="danger" %}
The destination of a transition is handled as an attribute of the transition named "destination".&#x20;

Therefore:

* Using this command multiple times for the same transition will only keep the latest state name.
* JARVIS4SE does not allow to define a new attribute named "destination"
{% endhint %}

#### Condition definition

JARVIS4SE allows to add a transition condition _\<transition condition value>_ for a transition named <_transition name_> through the following command:

```
Condition for <transition name> is: <transition condition value>
```

{% hint style="danger" %}
Two transition conditions for the same transition differs only in their syntax.

For exemple, the transition conditions "VOLTAGE > 7V" and "VOLTAGE > 7 V" are considered to be different conditions.
{% endhint %}

### Context visualization

JARVIS4SE allows to visualize the context of a state named _\<state name>_ through the following command:

```
show context <state name>
```

Below an example of a context visualization for a state S0 linked to a state S1 by a transition condition "VOLTAGE > 7V" with PlantUML:

```
S0 is a state
S1 is a state
T_S0_S1 is a transition
Condition for T_S0_S1 is: VOLTAGE > 7V
The source of T_S0_S1 is S0
The destination of T_S0_S1 is S1
show context S0
```

<figure><img src="../../.gitbook/assets/image (6).png" alt=""><figcaption></figcaption></figure>

### Chain visualization

JARVIS4SE allows to visualize a chain of states named _\<state i name>_, linked together by the transitions for which the source and the destination are one of these states, through the following command:

```
show chain <state 1 name>, <state 2 name>
```

{% hint style="info" %}
Chain visualization could be equivalent to a:

* Context visualization in case of dealing with the same states
* Decomposition visualization in case of dealing with the chain of all substates of the same state.
{% endhint %}

Below an example of a chain visualization with the previous S0 and S1 states and the following additional elements:

* A new state S2
* A new transition T\_S1\_S0
* A new transition T\_S1\_S2

```
S2 is a state

T_S1_S0 is a transition
Condition for T_S1_S0 is: VOLTAGE < 6V
The source of T_S1_S0 is S1
The destination of T_S1_S0 is S0

T_S1_S2 is a transition
The source of T_S1_S2 is S1
The destination of T_S1_S2 is S2
Condition for T_S1_S2 is: BUS_COMMUNICATION_STATUS == BUS_COMMUNICATION_ON

show chain S1, S2
```

<figure><img src="../../.gitbook/assets/image (4) (1).png" alt=""><figcaption></figcaption></figure>

## Functional element state decomposition

### Child definition

JARVIS4SE allows to decompose a state named \<state name> into substates named _\<substate i name>_ through one of the following commands:

```
<state name> is composed of <substate 1 name>, <substate 2 name>
```

```
<substate 1 name> composes <state name>
```

```
<substate 1 name>, <substate 2 name> compose <state name>
```

{% hint style="info" %}
The substates must be created before as states. Please refer to the chapter [#functional-element-state-creation](functional-architecture-definition.md#functional-element-state-creation "mention")
{% endhint %}

### Decomposition visualization

JARVIS4SE allows to visualize the decomposition of a state named _\<state name>_ through the following command:

```
show decomposition <state name>
```

Below an exemple of a decomposition of the previous state S1 into S11 and S12 with a dedicated transition between the two substates with PlantUML:

```
S11 is a state
S12 is a state
T_S11_S12 is a transition
The source of T_S11_S12 is S11
The destination of T_S11_S12 is S12
S1 is composed of S11, S12

show decomposition S1
```

{% hint style="danger" %}
This function is not yet available.\
Please refer to [https://github.com/rcasteran/jarvis4se/issues/88](https://github.com/rcasteran/jarvis4se/issues/88)
{% endhint %}

## Functional element state allocation

JARVIS4SE allows to allocate a state named \<state name> to a functional element named \<functional element name> through one of the following commands:

```
<functional element name> allocates <state name>
```

```
 <state name> is allocated to <functional element name>
```

{% hint style="info" %}
When allocating a state to a functional element, all the state children are also allocated to this functional element. This allow to allocate these state children to the functional element children if any.
{% endhint %}

## Functional element state machine

JARVIS4SE allows to visualize the state machine of a functional element named _\<functional element name_> through the following command:

```
show state <functional element name>
```

The state machine of a functional element comprises all the states allocated to this functional element and their related transitions.

Below an example of the state machine of the previous functional element E which allocates the previous S0 and S1 states and the following additional states with PlantUML:

* SE as an entry state with a transition to S0
* S2 as a state with a transition from S1
* SF as an exit state with a transition from S2

<pre><code><strong>"Entry state" extends state
</strong>"Exit state" extends state
SE is an Entry state
SF is an Exit state

T_SE_S0 is a transition
The source of T_SE_S0 is SE
The destination of T_SE_S0 is S0

T_S2_SF is a transition
The source of T_S2_SF is S2
The destination of T_S2_SF is SF

E allocates SE, S0, S1, S2, SF

show state E
</code></pre>

<figure><img src="../../.gitbook/assets/image (5) (1).png" alt=""><figcaption></figcaption></figure>

## Function allocation

### Allocation to functional element

JARVIS4SE allows to allocate a function named \<function name> to a functional element named \<functional element name> through one of the following commands:

```
<functional element name> allocates <function name>
```

```
<function name> is allocated to <functional element name>
```

{% hint style="info" %}
When allocating a function to a functional element, all the function children are also allocated to this functional element. This allows to allocate these function children to the functional element children if any.
{% endhint %}

Below an example of the allocation of a function F to the previous functional element E:

```
F is a function
x is a data
y is a data
F consumes x
F produces y
E allocates F

show decomposition E
```

<figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption></figcaption></figure>

### Allocation to functional element state

JARVIS4SE allows to allocate a function named \<function name> to a state named \<state name> through one of the following commands:

```
<state name> allocates <function name>
```

```
<function name> is allocated to <state name>
```

{% hint style="danger" %}
When allocating a function to a state, if the function is allocated to a functional element, then the state is allocated to this functional element.&#x20;

Reversewise, when allocating a function to a state, if the state is allocated to a functional element, then the function is allocated to this functional element.
{% endhint %}

## Data allocation

JARVIS4SE allows to allocate a data named \<data name> to a functional interface named \<functional interface name> through one of the following commands:

```
<functional interface name> allocates <data name>
```

```
<data name> is allocated to <functional interface name>
```

{% hint style="info" %}
Data is allocated to the functional interface only if one of its consumer and one of its producer are allocated to a functional element exposing the functional interface. Please refer to [#function-allocation](functional-architecture-definition.md#function-allocation "mention")
{% endhint %}

Below an example of the allocation of the data x, consumed by the previous function F allocated to the functional element E, to the interface I which is exposed by the functional element EE1 with a function F1 which produces the data x:

```
EE1 is a functional element
F1 is a function
EE1 allocates F1

EE1 exposes I
F1 produces x

I allocates x

show context E
```

<figure><img src="../../.gitbook/assets/image (1) (1).png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
Please note that JARVIS4SE will warn you in case one functional element exposing the interface has a functional element child that exposes it, suggesting you to allocate the related function to this child.
{% endhint %}

In the previous example, JARVIS4SE will warn you that functional element E1 is also exposing the interface I, suggesting you to allocate the function F to it.

## Requirement satisfaction

### Requirement satisfied by a functional element

JARVIS4SE allows to indicate that a functional element named \<functional element name> satisfies a requirement named \<requirement name> through one of the following commands:

```
<functional element name> satisfies <requirement name>
```

```
<requirement name> is satisfied by <functional element name>
```

### Requirement satisfied by a functional interface

JARVIS4SE allows to indicate that a functional interface named \<functional interface name> satisfies a requirement named \<requirement name> through one of the following commands:

```
<functional interface name> satisfies <requirement name>
```

```
<requirement name> is satisfied by <functional interface name>
```

## Functional architecture chain

### Chain visualization

JARVIS4SE allows to visualize a chain of functional element named _\<function element i name>,_ linked together by the data produced/consumed by the functions allocated to them, through the following command:

```
show chain <functional element 1 name>, <functional element 2 name>
```

Below an example of a chain visualization with the previous functional element E and EE1:

<figure><img src="../../.gitbook/assets/image (2) (1).png" alt=""><figcaption></figcaption></figure>

### Sequence visualization

JARVIS4SE allows to  visualize a chain of functional elements named _\<function element i name>,_ linked together by the data produced/consumed by the functions allocated to them, as a sequence of functional elements, through the following command:

```
show sequence <functional element 1 name>, <functional element 2 name>
```

Below an example of a sequence visualization with the previous E and EE1 functional elements:

<figure><img src="../../.gitbook/assets/image (3) (1).png" alt=""><figcaption></figcaption></figure>

JARVIS4SE allows to visualize also a chain of functional elements that expose a functional interface named _\<functional interface name>_ as a sequence of functional elements throught the following command:

```
show sequence <functional interface name>
```

Below an example of a sequence visualization for the interface I between the previous E and EE1 functional elements:

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
Please note that JARVIS4SE will warn you in case one functional element exposing the interface has a functional element child that exposes it, suggesting you to allocate the related function to this child.
{% endhint %}

In the previous example, JARVIS4SE will warn you that functional element E has a child that is also exposing the interface I, suggesting you to allocate the function F to it.
