# Just Another Rather Very Intelligent System (JARVIS) for Systems Engineers (SE)

Latest stable release: ![GitHub release (latest by date)](https://img.shields.io/github/v/release/rcasteran/jarvis4se)

Current CI status: [![CircleCI](https://circleci.com/gh/rcasteran/jarvis4se/tree/main.svg?style=svg)](https://circleci.com/gh/rcasteran/jarvis4se/tree/main)

Playground (with latest stable release) : [![Binder](https://mybinder.org/badge\_logo.svg)](https://mybinder.org/v2/gh/Not2behere/PlayJarvis4se/HEAD)

## Introduction

JARVIS4SE allows systems engineers to build the single source of truth of the knowledge they develop about the system of interest they want to master, preventing this knowledge from being:

* Distorted by any graphical representation considerations
* Splitted accross different domain languages
* Expressed only in a machine readable medium

### Free from graphical representation considerations

The core of JARVIS4SE is independent from any graphical representation considerations: it is based on a set of basic [engineering concepts](docs/engineering-concepts/definitions.md) adapted from different domain languages, without taking into account concepts like coordinates, rendering...

To be able to visualize the knowledge of the system of interest with diagrams, the core of JARVIS4SE can be interfaced with the API of any modeling tool through a dedicated adapter.

Today the following adapters are available:

* [PlantUML](https://plantuml.com/en/)

### Based on natural language

The core of JARVIS4SE is based on a subset of the english language that has been mapped to the set of basic [engineering concepts](docs/engineering-concepts/definitions.md).

This allows systems engineers to interact with JARVIS4SE via voice or a textual interface.
