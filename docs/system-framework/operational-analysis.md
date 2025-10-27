# Operational analysis

Operational analysis is the systematic examination of a defined <mark style="color:blue;">activity</mark> to identify how it influences the system definition or usage, in which operational situation it occurs and under which conditions (Adapted from <mark style="color:blue;">REF\_2</mark>)

From a methodological point of view, the definition of an activity can be justified by:

* The documentation of a goal specifying the related <mark style="color:blue;">operational situation</mark>;
* The identification of a new <mark style="color:blue;">data</mark> to be created / transformed during the functional analysis.

## Information creation

### Definition

JARVIS4SE allows to define a new information named _\<information name>_ through the following command:

```
<information name> is an information
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for an information named _\<information name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <information name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the information.

{% hint style="info" %}
The first command is only required when the attribute does not exist
{% endhint %}

## Activity creation

### Definition

JARVIS4SE allows to define a new activity named _\<activity name>_ through the following command:

```
<activity name> is an activity
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for an activity named _\<activity name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <activity name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the activity.

{% hint style="info" %}
The first command is only required when the attribute does not exist
{% endhint %}

### Information consumption

JARVIS4SE allows to indicate that an information named _\<information name>_ is consumed by an activity named _\<activity name>_ through one of the following commands:

```
<activity name> consumes <information name>
```

```
<information name> is an input of <activity name>
```

### Information production

JARVIS4SE allows to indicate that an information named _\<information name>_ is produced by an activity named _\<activity name>_ through one of the following commands:

```
<activity name> produces <information name>
```

```
<information name> is an output of <activity name>
```

### Context visualization

JARVIS4SE allows to visualize the context of an activity named _\<activity name>_ through the following command:

```
show context <activity name>
```

Below an example of a context visualization for an activity A defined as followed: info\_b = A(info\_a) with PlantUML:

```
A is an activity
info_a is an information
A consumes info_a
info_b is an information
A produces info_b
show context A
```

<figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

## Activity decomposition

{% hint style="warning" %}
An activity cannot be decomposed
{% endhint %}

## Goal satisfaction

### Goal satisfied by an activity

JARVIS4SE allows to indicate that an activity named \<activity name> satisfies a goal named \<goal name> through one of the following commands:

<pre><code><strong>&#x3C;activity name> satisfies &#x3C;goal name>
</strong></code></pre>

```
<goal name> is satisfied by <activity name>
```

## Operational chain

### Chain visualization

JARVIS4SE allows to visualize a chain of activities named _\<activity i name>,_ linked together by the information they produce/consume, through the following command:

```
show chain <activity 1 name>, <activity 2 name>
```

Below an example of a chain visualization with the previous activity A and a new activity B:

```
B is an activity
B consumes info_b

info_c is an information
B produces info_c

show chain A, B
```

<figure><img src="../../.gitbook/assets/image (1).png" alt=""><figcaption></figcaption></figure>

### Sequence visualization

JARVIS4SE allows to visualize a chain of activities named _\<activity i name>,_ linked together by the information they produce/consume, as a sequence of activities, through the following command:

```
show sequence <activity 1 name>, <activity 2 name>
```

Below an example of a sequence visualization with the previous A and B activities:

```
show sequence A, B
```

<figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>
