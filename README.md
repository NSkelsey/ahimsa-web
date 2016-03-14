ahimsa-web
==========

Web frontend for messages stored in the blockchain. This services relies on a [ombwebrelay](https://github.com/soapboxsys/ombudslib/tree/master/cmds/ombwebrelay) server hosting content at `localhost:1055` by default. ahimsa-web can be configured to use external servers like `http://ox.nskelsey.com/` by modifying `settings.py`

Requirements
============

- Python 2.7
- Pip
- VirtualEnv


Installation
============

```bash
> git clone https://github.com/NSkelsey/ahimsa-web && cd ahimsa-web
> virtualenv venv
> source venv/bin/activate
> pip install -r requirements.txt
> python app.py runserver
```
