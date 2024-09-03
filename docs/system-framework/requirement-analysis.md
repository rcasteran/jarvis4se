# Requirement analysis

Requirement analysis is the systematic examination of a [goal](broken-reference) expressed by at least one stakeholder to identify all the [requirement](broken-reference)s the [system ](broken-reference)must satisfy to achieve it.

From a methodological point of view:

* A goal is achieved by an [activity](broken-reference) that can be performed by the [system](broken-reference), an [actor](broken-reference) or an [enabling system](broken-reference). If the goal cannot be achieved by a single activity, then it can be refined into different subgoals up to identify an activity for each subgoal in the [operational analysis](operational-analysis.md).A goal is satisfied if all subgoals are satisfied (AND-decomposition) or if at least one subgoal is satisfied (OR-decomposition)
* A goal can be in conflict with another goal: in this case only one of the two goals can be achieved by an activity
* A requirement is specifying a behavior or a quality of the activity to be perfomed to achieve a goal. A requirement that specifies a behavior or a quality of an activity performed by the system can be derived into different subrequirements up to identify a system element in the [physical architecture definition](physical-architecture-definition.md).

## Goal creation

### Goal definition

### Goal attributes

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

### Text definition

JARVIS4SE allows to define the text _\<requirement\_text>_ of a requirement named _\<requirement name>_ through the following command:

```
The text of <requirement_name> is <requirement_text>
```

{% hint style="danger" %}
The text of a requirement is handled as an attribute of the requirement named "text".\
Therefore:

* Using this command multiple times for the same requirement will only keep the latest text value.
* JARVIS4SE does not allow to define a new attribute named "text"
{% endhint %}

{% hint style="info" %}
The text of a requirement must be a sentence containing the modal "shall".
{% endhint %}

## Requirement decomposition

## Requirement import/export

### CSV import/export
