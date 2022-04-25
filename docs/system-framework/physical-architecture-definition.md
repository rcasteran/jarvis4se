# Physical architecture definition

Physical architecture is the systematic examination of the different architecture candidates to identify the [physical elements](../engineering-concepts/definitions.md) and their required [physical interfaces](../engineering-concepts/definitions.md) which implements through technologies the selected [functional architecture](functional-architecture-definition.md), and to select the best one according to the selected architecture criteria (Adapted from [REF\_3](../engineering-concepts/references.md))

## Physical interface creation

### Definition

JARVIS4SE allows to define a new physical interface named _\<physical interface name>_ through the following command:

```
<physical interface name> is a physical interface
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a physical interface named _\<physical interface name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <physical interface name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the physical interface.

<mark style="color:orange;">Note: the first command is only required when the attribute does not exist.</mark>

### Interaction visualization

TBD

## Physical element creation

### Definition

JARVIS4SE allows to define a new physical element named _\<physical element name>_ through the following command:

```
<physical element name> is a physical element
```

### Attributes

JARVIS4SE allows to define an attribute named _\<attribute name>_ for a physical element named _\<physical element name>_ through the following commands:

```
<attribute name> is an attribute
The <attribute name> of <physical element name> is <attribute value>
```

The definition of an attribute implies to assign a value _\<attribute value>_ that characterizes the physical element.

<mark style="color:orange;">Note: the first command is only required when the attribute does not exist.</mark>

### Physical interface exposure

JARVIS4SE allows to indicate that a physical interface named _\<physical interface name>_ is exposed by a physical element named _\<physical element name>_ through the following command:

```
<physical element name> exposes <physical interface name>
```

### Context visualization

JARVIS4SE allows to visualize the context of a physical element named _\<physical element name>_ through the following command:

```
show context <physical element name>
```

Below an example of a context visualization for a functional element E which exposes an interface I with PlantUML:

```
E is a physical element
I is a physical interface
E exposes I
show context E
```

## Physical element decomposition

### Child definition

JARVIS4SE allows to decompose a physical element named _\<physical element name>_ into physical subelements named _\<physical subelement i name>_ through the following command:

```
<physical element name> is composed of <physical subelement 1 name>, <physical subelement 2 name>
```

<mark style="color:orange;">Note: the physical subelements must be created before as physical elements</mark>. Please refer to chapter [#physical-element-creation](physical-architecture-definition.md#physical-element-creation "mention")

### Decomposition visualization

JARVIS4SE allows to visualize the decomposition of a physical element named _\<physical element name>_ through the following command:

```
show decomposition <physical element name>
```

Below an example of a decomposition of the previous physical element E (which exposes I) into E1 (which exposes I and I1) and E2 (which exposes I1) with PlantUML:

```
E1 is a physical element
I1 is a physical interface
E1 exposes I
E1 exposes I1
E2 is a physical element
E2 exposes I1
E is composed of E1, E2
show decomposition E
```

## Functional interface allocation

## Functional element allocation

### Allocation to actor

### Allocation to physical element

## Requirement allocation

### Allocation to Physical interface

### Allocation to Physical element

## Physical chain
