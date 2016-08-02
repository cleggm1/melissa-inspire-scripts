#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2016 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Bibcheck plugin to add 980__a type-codes to records from journals that always 
    contain published, conference, or review papers
"""

from invenio.search_engine import perform_request_search, get_fieldvalues

JOURNAL_PUBLISHED_DICT = {"Ann.Rev.Astron.Astrophys.":"10.1146/annurev-astro",
"Astron.Astrophys.":"10.1051/0004-6361/",
"Astron.J.":"10.1088/0004-6256/",
"Astron.Astrophys.Suppl.Ser.":None,
"Astrophys.J.":"10.1088/0004-637X/",
"Astrophys.J.Suppl.":"10.1088/0067-0049/",
"Europhys.Lett.":"10.1209/0295-5075",
"JHEP":"10.1007/JHEP",
"Mon.Not.Roy.Astron.Soc.":"10.1093/mnras",
"Nature":"10.1038/nature",
"Nature Phys.":"10.1038/nphys",
#"Nucl.Phys.":"10.1016/j.nuclphysb.",
"Phys.Lett.":"10.1016/j.physletb.",
"Phys.Rept.":"10.1016/j.physrep.",
"Phys.Rev.":"10.1103/PhysRevD.",
"Phys.Rev.Lett.":"10.1103/PhysRevLett.",
"Rev.Mod.Phys.":"10.1103/RevModPhys.",
"Science":"10.1126/science"}

CONFERENCE_DICT = {"AIP Conf.Proc.":None,
"ASP Conf.Ser.":None,
"EPJ Web Conf.":"10.1051/epjconf",
"J.Phys.Conf.Ser.":"10.1088/1742-6596",
"Int.J.Mod.Phys.Conf.Ser.":None,
"Nucl.Phys.Proc.Suppl.":"10.1016/j.nuclphysbps."
}

REVIEW_DICT = {"Prog.Part.Nucl.Phys.":"10.1016/j.ppnp.",
"Phys.Rept.":"10.1016/j.physrep.",
"Cambridge Monogr.Math.Phys.":None,
"Ann.Rev.Nucl.Part.Sci.":None,
"Ann.Rev.Astron.Astrophys.":None,
"Ann.Rev.Phys.Chem.":None,
"Ann.Rev.Fluid Mech.":None,
"Ann.Rev.Earth Planet.Sci.":None,
"Ann.Rev.Psych.":None,
"Ann.Rev.Mater.Sci.":None,
"Ann.Rev.Physiol.":None,
"Ann.Rev.Biophys.Biomol.Struct.":None,
"Ann.Rev.Condensed Matter Phys.":None,
"Ann.Rev.Biophys.":None,
"Ann.Rev.Biophys.Bioeng.":None,
"Rept.Prog.Phys.":"10.1088/0034-4885",
"Rev.Phys.":"10.1016/j.revip.",
"Living Rev.Sol.Phys.":None,
"Living Rev.Rel.":None,
"Space Sci.Rev.":"10.1007/s11214",
"Rev.Mod.Phys.":"10.1103/RevModPhys.",
"Astron.Astrophys.Rev.":"10.1007/s00159",
"Rev.Accel.Sci.Tech.":"10.1142/S17936268"
}

type_codes = ['Published', 'Review', 'ConferencePaper']

def add_code(record, type_code, journals, dois, codes):
    add_type_code = False
    if type_code == 'Published':
        if type_code not in codes:
            for key, val in JOURNAL_PUBLISHED_DICT:
                if key in journals or val in dois:
                    add_type_code = True
    if type_code == 'ConferencePaper':
        if type_code not in codes:
            for key, val in CONFERENCE_DICT:
                if key in journals or val in dois:
                    add_type_code = True
    if type_code == 'Review':
        if type_code not in codes:
            for key, val in REVIEW_DICT:
                if key in journals or val in dois:
                    add_type_code = True
    if add_type_code:
        record.add_field('980__', '', subfields=[('a', type_code)]

def check_record(record):
    journals = get_fieldvalues(record, '773__p')
    dois = get_fieldvalues(record, '0247_a')
    codes = get_fieldvalues(record, '980__a')
    for type_code in type_codes:
        add_code(record, type_code, journals, dois, codes)
