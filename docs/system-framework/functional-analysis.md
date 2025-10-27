# Functional analysis

Functional analysis is the systematic examination of a defined [function](../engineering-concepts/definitions.md) to identify all the subfunctions necessary to accomplish that function and to identify the incoming / outgoing [data](../engineering-concepts/definitions.md) flowing between them (adapted from [REF\_3](../engineering-concepts/references.md))

From a methodological point of view, the definition of a function can be justified by:

* The documentation of a [requirement](../engineering-concepts/definitions.md) specifying its behavior or its quality;
* The refinement of an [activity](../engineering-concepts/definitions.md) identified during the operational analysis;
* The identification of new data to be created / transformed during the definition of the functional architecture and/or the physical architecture.

## Data creation

### Definition

JARVIS4SE allows to define a new data named _\<data name>_ through the following command:

```
<data name> is a data
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a data named _\<data name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <data name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the data.

{% hint style="info" %}
The first command is only required when the attribute does not exist
{% endhint %}

### Information allocation

JARVIS4SE allows to allocate an information named \<information name> to a data named \<data name> through one of the following commands:

```
<data name> allocates <information name>
```

```
<information name> is allocated to <data name>
```

## Function creation

### Definition

JARVIS4SE allows to define a new function named _\<function name>_ through the following command:

```
<function name> is a function
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a function named _\<function name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <function name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the function.

{% hint style="info" %}
The first command is only required when the attribute does not exist
{% endhint %}

### Data consumption

JARVIS4SE allows to indicate that a data named _\<data name>_ is consumed by a function named _\<function name>_ through one of the following commands:

```
<function name> consumes <data name>
```

```
<data name> is an input of <function name>
```

### Data production

JARVIS4SE allows to indicate that a data named _\<data name>_ is produced by a function named _\<function name>_ through one of the following commands:

```
<function name> produces <data name>
```

```
<data name> is an output of <function name>
```

### Context visualization

JARVIS4SE allows to visualize the context of a function named _\<function name>_ through the following command:

```
show context <function name>
```

Below an example of a context visualization for a function F defined as followed: y = F(x) with PlantUML:

```
F is a function
x is a data
F consumes x
y is a data
F produces y
show context F
```

![](<../../.gitbook/assets/image (1) (1) (1) (1) (1).png>)

## Function decomposition

### Child definition

JARVIS4SE allows to decompose a function named _\<function name>_ into subfunctions named _\<subfunction i name>_ through one of the following commands:

```
<function name> is composed of <subfunction 1 name>, <subfunction 2 name>
```

```
<subfunction 1 name> composes <function name>
```

```
<subfunction 1 name>, <subfunction 2 name> compose <function name>
```

{% hint style="info" %}
The subfunctions must be created before as functions. Please refer to chapter [#function-creation](functional-analysis.md#function-creation "mention")
{% endhint %}

### Decomposition visualization

JARVIS4SE allows to visualize the decomposition of a function named _\<function name>_ through the following command:

```
show decomposition <function name>
```

Below an example of a decomposition of the previous function F (defined as followed: y = F(x)) into F1 (defined as followed:  a = F1(x)) and F2 (defined as followed: y = F2(a)) with PlantUML:

```
F1 is a function
a is a data
F1 consumes x
F1 produces a
F2 is a function
F2 consumes a
F2 produces y
F is composed of F1, F2
show decomposition F
```

![](<../../.gitbook/assets/image (3) (1) (1).png>)

## Activity allocation

JARVIS4SE allows to allocate an activity named \<activity name> to a function named \<function name> through one of the following commands:

```
<function name> allocates <activity name>
```

```
<activity name> is allocated to <function name>
```

## Requirement satisfaction

### Requirement satisfied by a function

JARVIS4SE allows to indicate that a function named \<function name> satisfies a requirement named \<requirement name> through one of the following commands:

<pre><code><strong>&#x3C;function name> satisfies &#x3C;requirement name>
</strong></code></pre>

```
<requirement name> is satisfied by <function name>
```

### Requirement satisfied by a data

JARVIS4SE allows to indicate that a data named \<data name> satisfies a requirement named \<requirement name> through one of the following commands:

```
<data name> satisfies <requirement name>
```

```
<requirement name> is satisfied by <data name>
```

## Functional chain

### Chain visualization

JARVIS4SE allows to visualize a chain of functions named _\<function i name>,_ linked together by the data they produce/consume, through the following command:

```
show chain <function 1 name>, <function 2 name>
```

{% hint style="info" %}
Chain visualization could be equivalent to a decomposition visualization in case of dealing with the chain of all subfunctions of the same function.
{% endhint %}

Below an example of a chain visualization with the previous F1 and F2 subfunctions:

```
show chain F1, F2
```

<figure><img src="../../.gitbook/assets/image (2) (1) (1).png" alt=""><figcaption></figcaption></figure>

### Sequence visualization

JARVIS4SE allows to visualize a chain of functions named _\<function i name>,_ linked together by the data they produce/consume, as a sequence of functions, through the following command:

```
show sequence <function 1 name>, <function 2 name>
```

Below an example of a sequence visualization with the previous F1 and F2 subfunctions:

```
show sequence F1, F2
```

![](<../../.gitbook/assets/image (3) (1) (1) (1).png>)
