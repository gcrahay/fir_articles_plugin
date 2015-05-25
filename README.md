# Knowledge bas articles plugin for FIR - Fast Incident Response

[FIR](https://github.com/certsocietegenerale/FIR) (Fast Incident Response by [CERT Société générale](https://cert.societegenerale.com/)) is an cybersecurity incident management platform designed with agility and speed in mind. It allows for easy creation, tracking, and reporting of cybersecurity incidents.


# Features

This plugins allows you to manage a knowledge base in FIR. Articles share many features with events, like artifacts. Articles artifacts can be correlated with events artifacts.

# Installation

**Warning: This plugin needs some features not merged in the FIR official repository. PRs will be submitted soon!**

## Overview

Follow the generic plugin installation instructions in [the FIR wiki](https://github.com/certsocietegenerale/FIR/wiki/Plugins).
Make sure the following line is included in the `urlpatterns` variable in `fir/urls.py`:

```
url(r'^articles/', include('fir_articles.urls', namespace='articles')),

```

## Details

You should install it in the FIR _virtualenv_. 

```bash
(your_env)$ git clone https://github.com/gcrahay/fir_articles_plugin.git
(your_env)$ cd fir_articles_plugin
(your_env)$ python setup.py install

```

Make sure the following line is included in the `urlpatterns` variable in `fir/urls.py`:

```
url(r'^articles/', include('fir_articles.urls', namespace='articles')),

```

In your *$FIR_HOME*, launch:

```bash
(your_env)$ ./manage.py migrate
```

# Usage

This plugin adds a new entry in the main navbar named `Árticles`.

# Configuration

## User permissions

* *access_articles*: User can read articles 
* *modify_articles*: User can add or edit articles
