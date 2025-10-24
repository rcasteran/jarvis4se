# Requirement analysis

Requirement analysis is the systematic examination of a [goal](broken-reference) expressed by at least one stakeholder to identify all the [requirement](broken-reference)s the [system ](broken-reference)must satisfy to achieve it.

From a methodological point of view:

* A goal is achieved by an [activity](broken-reference) that can be performed by the [system](broken-reference), an [actor](broken-reference) or an [enabling system](broken-reference). If the goal cannot be achieved by a single activity, then it can be refined into different subgoals up to identify an activity for each subgoal in the [operational analysis](operational-analysis.md). A goal is satisfied if all subgoals are satisfied (AND-decomposition) or if at least one subgoal is satisfied (OR-decomposition)
* A goal can be in conflict with another goal: in this case only one of the two goals can be achieved by an activity
* A requirement is specifying a behavior or a quality of the activity to be perfomed to achieve a goal. A requirement that specifies a behavior or a quality of an activity performed by the system can be derived into different sub-requirements up to identify a system element in the [physical architecture definition](physical-architecture-definition.md).

## Goal creation

### Definition

JARVIS4SE allows to define a new goal named <_goal name>_ through the following command:

```
<goal name> is a goal
```

{% hint style="info" %}
JARVIS4SE detects automatically a goal when using a command following the requirement text structure. Please refer to [#text](requirement-analysis.md#text "mention")
{% endhint %}

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a goal named _\<goal name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <goal name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the goal.

{% hint style="info" %}
The first command is only required when the attribute does not exist.
{% endhint %}

### Text

JARVIS4SE allows to define the text _\<goal\_text>_ of a goal named _\<goal name>_ through the following command:

```
The text of <goal_name> is <goal_text>
```

{% hint style="warning" %}
The text of a goal is handled as an attribute of the goal named "text".\
Therefore:

* Using this command multiple times for the same goal will only keep the latest text value.
* JARVIS4SE does not allow to define a new attribute named "text"
{% endhint %}

JARVIS4SE allows to structure the text _\<goal\_text>_ to define actor, subject and activity related to the goal as follows:

| Goal   | Boilerplate                                                                       | Example                                                             |
| ------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Simple | **As a** _\<actor name>_, **I want** _\<subject name>_ **to** _\<activity name>_. | **As a** system engineer, **I want** JARVIS4SE **to** manage goals. |

{% hint style="info" %}
If a concept named \<actor name>, \<subject name> or \<activity name> already exists, and if this concept supports goal allocation, then JARVIS4SE will automatically allocate the goal to this concept.
{% endhint %}

## Goal decomposition

### AND-decomposition

### OR-decomposition

## Goal relationship

### Goal conflict

## Requirement creation

### Definition

JARVIS4SE allows to define a new requirement named _\<requirement name>_ through the following command:

```
<requirement name> is a requirement
```

{% hint style="info" %}
JARVIS4SE detects automatically a requirement when using a command following the requirement text structure. Please refer to [#text-1](requirement-analysis.md#text-1 "mention")
{% endhint %}

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a requirement named _\<requirement name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <requirement name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the requirement.

{% hint style="info" %}
The first command is only required when the attribute does not exist.
{% endhint %}

### Text

JARVIS4SE allows to define the text _\<requirement\_text>_ of a requirement named _\<requirement name>_ through the following command:

```
The text of <requirement_name> is <requirement_text>
```

{% hint style="warning" %}
The text of a requirement is handled as an attribute of the requirement named "text".\
Therefore:

* Using this command multiple times for the same requirement will only keep the latest text value.
* JARVIS4SE does not allow to define a new attribute named "text"
{% endhint %}

{% hint style="info" %}
The text of a requirement must be a sentence containing the modal "shall".
{% endhint %}

JARVIS4SE allows to structure the text _\<requirement\_text>_ to define conditions and temporality of the requirement as follows:

| Requirement                     | Boilerplate                                                                                              | Example                                                                                                                   |
| ------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Simple                          | _\<subject name>_ **shall** _\<object>_.                                                                 | The system **shall** open the door.                                                                                       |
| With conditions                 | **If** _\<condition list>_, **then** _\<subject name>_ **shall** _\<object>_.                            | **If** the system detects an emergency stop, **then** the system **shall** open the door.                                 |
| With temporality only           | **When** _\<temporality>_, _\<subject name>_ **shall** _\<object>_.                                      | **When** the system is stopped, the system **shall** open the door.                                                       |
| With conditions and temporality | **When** _\<temporality>_, **if** _\<condition list>_, **then** _\<subject name>_ **shall** _\<object>_. | **When** the system is stopped, **if** the system detects an emergency stop, **then** the system **shall** open the door. |

{% hint style="info" %}
If a concept named \<subject name> already exists, and if this concept supports requirement allocation, then JARVIS4SE will automatically allocate the requirement to this concept.
{% endhint %}

{% hint style="info" %}
If a concept is named in \<object>, \<condition list>, or \<temporality>, then JARVIS4SE will automatically allocate the requirement to this concept.
{% endhint %}

## Requirement decomposition

### Child definition

JARVIS4SE allows to derive a requirement named _\<requirement name>_ into derived requirements named _\<devreq i name>_ through one of the following commands:

```
<requirement name> is derived into <devreq 1 name>, <devreq 2 name>
```

```
<devreq 1 name> derives from <requirement name>
```

```
<devreq 1 name>, <devreq 2 name> derive from <requirement name>
```

{% hint style="info" %}
The derived requirements must be created before as requirements. Please refer to the chapter [#requirement-creation](requirement-analysis.md#requirement-creation "mention")
{% endhint %}

### Decomposition visualization

{% hint style="danger" %}
This function is not yet implemented.\
Please refer to [https://github.com/rcasteran/jarvis4se/issues/100](https://github.com/rcasteran/jarvis4se/issues/100)
{% endhint %}

## Requirement import/export

### CSV import/export
