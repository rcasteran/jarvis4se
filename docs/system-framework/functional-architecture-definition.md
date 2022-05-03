# Functional architecture definition

Functional architecture is the systematic examination of different implementation-independant architecture candidates to identify independent groups of [functions](../engineering-concepts/definitions.md) <mark style="color:blue;"></mark> and their required ressources to be executed (so called [functional elements](../engineering-concepts/definitions.md)) from the [functional analysis](functional-analysis.md), to organize the way they exchange [data](../engineering-concepts/definitions.md) (so called [functional interfaces](../engineering-concepts/definitions.md)), and to select the best one according to the selected architecture criteria (Adapted from [REF\_3](../engineering-concepts/references.md))

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

<mark style="color:orange;">Note: the first command is only required when the attribute does not exist.</mark>

### Interaction visualization

TBD

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

<mark style="color:orange;">Note: the first command is only required when the attribute does not exist.</mark>

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

## Functional element decomposition

### Child definition

JARVIS4SE allows to decompose a functional element named _\<functional element name>_ into functional subelements named _\<functional subelement i name>_ through the following command:

```
<functional element name> is composed of <functional subelement 1 name>, <functional subelement 2 name>
```

<mark style="color:orange;">Note: the functional subelements must be created before as functional elements</mark>. Please refer to chapter [#functional-element-creation](functional-architecture-definition.md#functional-element-creation "mention")

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

## Functional element state creation

### Transition definition

### State definition

### State context

### State attributes

## Data allocation

## Function allocation

### Allocation to functional element

### Allocation to functional element state

## Requirement allocation

## Functional architecture chain

