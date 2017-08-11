#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Perform HEP search on published only. For each record, get author list, citations/year total, citations/year by hep-th or hep-ex, citations/year from specific journals (make a dictionary of Q1, Q2, Q3, Q4 journals). From 

author list, figure out who are the phd students of each author. Then get cites/year excluding self-cites by the authors or by their 1st gen phd students. Then calculate average cites/year by hep-th or by hep-ex. Output 

everything in csv file.

Do we keep authorlist separate from students?

get_citers_log seems to count citations by when they are added to INSPIRE, not by what year the citation comes from



authorlist -> get name?, pid, figure out who their student is, get student's pid, get their all citations by them and their student
"""



from invenio.search_engine import perform_request_search, get_fieldvalues
from invenio.bibauthorid_dbinterface import get_author_by_canonical_name, get_canonical_name_of_author, get_personid_signature_association_for_paper
from invenio.bibedit_utils import get_bibrecord, record_get_field_values
import re
from pickle import dump


#search_term = "collection:published ('large nc' or 'large n-c' or 'large n c')"
search_term = "SUSY collection:published"
#search_term = "citedby:ea:C.M.Bouchard.1 ea:A.S.Kronfeld.1 d:2015"
#search_term = "ea:S.R.Sharpe.1 and citedby:ea:R.S.Van.de.Water.1 and d 2016"
#search_term = "recid:1338087"


Q1 = ('Phys.Rev.', 'Prog.Part.Nucl.Phys.', 'Ann.Rev.Nucl.Part.Sci.', 'Phys.Lett.', 'Prog.Nucl.Mag.Reson.Spectrosc.', 'Nucl.Phys.', 'Atom.Data Nucl.Data Tabl.','JHEAp', 'Annales Henri Poincare', 'J.Synchrotron Radiat.', 'JHEP', 'J.Phys.', 'J.Nucl.Mater.', 'Nucl.Eng.Des.', 'Ann.Rev.Astron.Astrophys.', 'Astron.Astrophys.Rev.', 'Astrophys.J.Suppl.', 'Ann.Rev.Earth Planet.Sci.', 'Phys.Dark Univ.', 'Living Rev.Sol.Phys', 'Astrophys.J.', 'Mon.Not.Roy.Astron.Soc.', 'Astron.J.', 'Astron.Astrophys.', 'Space Sci.Rev.', 'Publ.Astron.Soc.Pac.', 'Astropart.Phys.', 'New Astron.Rev.')
            
Q2 = ('Int.J.Mod.Phys.','Nucl.Fusion','J.Magn.Resonance', 'Phys.Rev.ST Accel.Beams', 'Nucl.Instrum.Meth.', 'High Energy Dens.Phys.', 'Adv.High Energy Phys.', 'Nucl.Data Sheets', 'Quant.Inf.Comput.', 'Int.J.Mod.Phys.', 'J.Nucl.Sci.Tech.', 'Mod.Phys.Lett.',   'IEEE Trans.Plasma Sci.', 'Icarus', 'Solar Phys.', 'Publ.Astron.Soc.Austral', 'Acta Astron.', 'Celest.Mech.Dyn.Astron.', 'Publ.Astron.Soc.Jap.', 'Exper.Astron.', 'Ann.Geophys.', 'JCAP', 'Bull.Astron.Soc.India', 'Planet.Space Sci.', 'Astrophys.Space Sci.', 'New Astron.', 'Res.Astron.Astrophys.', 'Astron.Nachr.', 'Int.J.Mod.Phys.', 'Mod.Phys.Lett.')

Q3 = ('IEEE Trans.Nucl.Sci.', 'Eur.Phys.J.', 'Hyperfine Interact.', 'Nucl.Technol.', 'J.Fusion Energ.', 'Phys.Part.Nucl.Lett.', 'Phys.Part.Nucl.', 'Radiophys.Quant.Electron.', 'Nucl.Part.Phys.Proc.', 'Synchrotron Radiat.News', 'Chin.Phys.', 'Phys.Atom.Nucl.', 'Adv.Astron.', 'J.Korean Astron.Soc.', 'Astron.Lett.', 'Geophys.Astrophys.Fluid Dynamics', 'Astron.Rep.', 'Rev.Mex.Astron.Astrofis', 'Astrophys.Space Sci.Trans', 'Baltic Astron.', 'Astrophys.Bull.', 'J.Astrophys.Astron.', 'Grav.Cosmol.', 'Sol.Syst.Res.')

Q4 = ('J.Neutron Res.', 'Adv.Imaging Electron Phys', 'Nucl.Phys.News', 'Prob.Atomic Sci.Technol.')

PAPERS = {}

def get_journal(recid):
    journals = get_fieldvalues(recid, '773__p')
    if journals:
        for j in journals:
            if j in Q1:
                return 'Q1'
            elif j in Q2:
                return 'Q2'
            elif j in Q3:
                return 'Q3'
            elif j in Q4:
                return 'Q4'
            

def get_fieldcode(recid):
    codes = get_fieldvalues(recid, '65017a')
    if 'Experiment-HEP' in codes:
        return 'HEP-EX'
    if 'Theory-HEP' in codes:
        return 'HEP-TH'


def get_date(recid):
    dates = get_fieldvalues(recid, '773__y')
    if len(dates) > 0:
        try_date = re.match('\d{4}', dates[0])
        if try_date:
            return int(try_date.group())
        else:
            return None

def main():
#   search_term = raw_input('INSPIRE search: ')
    search = perform_request_search(p=search_term, cc='HEP')
    for r in search:
        print "Working on", r
        PAPERS[r] = {'People':{'Student person IDs':[], 'Author person IDs':[]}, 'Citation logs':{'Including self-cites':{'Total':{}, 'HEP-EX':{}, 'HEP-TH':{}, 'Q1':{},  'Q2':{}, 'Q3':{}, 'Q4':{}},
		     		   'Excluding self-cites':{'Total':{}, 'HEP-EX': {}, 'HEP-TH':{}, 'Q1':{},  'Q2':{}, 'Q3':{}, 'Q4':{}}}}



# Get pids for authors of a paper. Is there a way to associate a pid with an author name?
        PAPERS[r]['People']['Author person IDs'] =[val for _, val in get_personid_signature_association_for_paper(r).iteritems()]
        canonical_names = []
# Get BAI of pid
        for pid in PAPERS[r]['People']['Author person IDs']:
            foo = get_canonical_name_of_author(pid)
            for x in foo:
                for y in x:
                    canonical_names.append(y)
# Find BAI in HEPNames, get INSPIRE-ID, find students of author, get BAIS, convert to pids, add to dict
        for bai in canonical_names:
            bai_search = perform_request_search(p='035__a:%s' % bai, cc='HepNames')
            if len(bai_search) == 1:
                for person in bai_search:
                    record = get_bibrecord(person)
                    inspireid = record_get_field_values(record, '035', code='a', filter_subfield_code='9', filter_subfield_value='INSPIRE')
                    if inspireid:
                        student_search = perform_request_search(p='701__i:%s' % inspireid[0], cc='HepNames')
                        if len(student_search) > 0:
                            for student in student_search:
                                srecord = get_bibrecord(student)
                                sbai = record_get_field_values(srecord, '035', code='a', filter_subfield_code='9', filter_subfield_value='BAI')
                                if sbai:
                                    try:
                                        student_pid = int(get_author_by_canonical_name(sbai)[0][0])
                                        PAPERS[r]['People']['Student person IDs'].append(student_pid)
                                    except IndexError:
                                        pass
            
        dates = []
# Get total citations of paper
        cite_search = perform_request_search(p='refersto:recid:%i collection:published ' % r, cc='HEP')
        for c in cite_search:
            xciteself = True
            xciteprof = True
# Get pids of citing authors, indicate whether citing paper is a self-cite
            citing_pids = [val for _, val in get_personid_signature_association_for_paper(c).iteritems()]
#            print 'authors', PAPERS[r]['People']['Author person IDs']
#            print 'students', PAPERS[r]['People']['Student person IDs']
#            print 'citing pids', citing_pids
#            print PAPERS[r]
            if not any(author in citing_pids for author in PAPERS[r]['People']['Author person IDs']):
                xciteself = False
            if not any(author in citing_pids for author in PAPERS[r]['People']['Student person IDs']):
                xciteprof = False
            date = get_date(c)
            dates.append(date)
            if date in PAPERS[r]['Citation logs']['Including self-cites']['Total']:
                PAPERS[r]['Citation logs']['Including self-cites']['Total'][date] += 1
            else:
                PAPERS[r]['Citation logs']['Including self-cites']['Total'][date] = 1
            
            if xciteself or xciteprof:
                if date in PAPERS[r]['Citation logs']['Excluding self-cites']['Total']:
                    PAPERS[r]['Citation logs']['Excluding self-cites']['Total'][date] += 1
                else:
                    PAPERS[r]['Citation logs']['Excluding self-cites']['Total'][date] = 1
# Get hep-ex or hep-th citations of paper
            fieldcode = get_fieldcode(c)
            if fieldcode:
                if date in PAPERS[r]['Citation logs']['Including self-cites'][fieldcode]:
                    PAPERS[r]['Citation logs']['Including self-cites'][fieldcode][date] += 1
                else:
                    PAPERS[r]['Citation logs']['Including self-cites'][fieldcode][date] = 1
                if xciteself or xciteprof:
                    if date in PAPERS[r]['Citation logs']['Excluding self-cites'][fieldcode]:
                        PAPERS[r]['Citation logs']['Excluding self-cites'][fieldcode][date] += 1
                    else:
                        PAPERS[r]['Citation logs']['Excluding self-cites'][fieldcode][date] = 1

# Separate Q1-4 citations
            journal_group = get_journal(r)
            if journal_group:
                if date in PAPERS[r]['Citation logs']['Including self-cites'][journal_group]:
                    PAPERS[r]['Citation logs']['Including self-cites'][journal_group][date] += 1
                else:
                    PAPERS[r]['Citation logs']['Including self-cites'][journal_group][date] = 1
                if xciteself or xciteprof:
                    if date in PAPERS[r]['Citation logs']['Excluding self-cites'][journal_group]:
                        PAPERS[r]['Citation logs']['Excluding self-cites'][journal_group][date] += 1
                    else:
                        PAPERS[r]['Citation logs']['Excluding self-cites'][journal_group][date] = 1

# put data in CSV format
#    csv_output = []
    for key, val in PAPERS.iteritems():
#get average cites/year
        total_avg = 0
        hepex_avg = 0
        hepth_avg = 0
        Q1_avg = 0
        Q2_avg = 0
        Q3_avg = 0
        Q4_avg = 0
        xtotal_avg = 0
        xhepex_avg = 0
        xhepth_avg = 0
        xQ1_avg = 0
        xQ2_avg = 0
        xQ3_avg = 0
        xQ4_avg = 0

        if sum(PAPERS[key]['Citation logs']['Including self-cites']['Total'].values()) > 0:
            total_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['Total'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['Total'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX'].values()) > 0:
            hepex_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH'].values()) > 0:
            hepth_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['Q1'].values()) > 0:
            Q1_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['Q1'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['Q1'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['Q2'].values()) > 0:
            Q2_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['Q2'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['Q2'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['Q3'].values()) > 0:
            Q3_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['Q3'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['Q3'])
        if sum(PAPERS[key]['Citation logs']['Including self-cites']['Q4'].values()) > 0:
            Q4_avg = sum(PAPERS[key]['Citation logs']['Including self-cites']['Q4'].values())/len(PAPERS[key]['Citation logs']['Including self-cites']['Q4'])

        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Total'].values()) > 0:
            xtotal_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Total'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['Total'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX'].values()) > 0:
            xhepex_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH'].values()) > 0:
            xhepth_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q1'].values()) > 0:
            xQ1_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q1'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['Q1'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q2'].values()) > 0:
            xQ2_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q2'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['Q2'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q3'].values()) > 0:
            xQ3_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q3'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['Q3'])
        if sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q4'].values()) > 0:
            xQ4_avg = sum(PAPERS[key]['Citation logs']['Excluding self-cites']['Q4'].values())/len(PAPERS[key]['Citation logs']['Excluding self-cites']['Q4'])
      
        PAPERS[key]['Citation logs']['Including self-cites']['Total']['Average'] = total_avg
        PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX']['Average'] = hepex_avg
        PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH']['Average'] = hepth_avg
        PAPERS[key]['Citation logs']['Including self-cites']['Q1']['Average'] = Q1_avg
        PAPERS[key]['Citation logs']['Including self-cites']['Q2']['Average'] = Q2_avg
        PAPERS[key]['Citation logs']['Including self-cites']['Q3']['Average'] = Q3_avg
        PAPERS[key]['Citation logs']['Including self-cites']['Q4']['Average'] = Q4_avg

        PAPERS[key]['Citation logs']['Excluding self-cites']['Total']['Average'] = xtotal_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX']['Average'] = xhepex_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH']['Average'] = xhepth_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['Q1']['Average'] = xQ1_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['Q2']['Average'] = xQ2_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['Q3']['Average'] = xQ3_avg
        PAPERS[key]['Citation logs']['Excluding self-cites']['Q4']['Average'] = xQ4_avg

    with open('bubble_SUSY.dict', 'wb') as dict_out:
        dump(PAPERS, dict_out)

               
#        csv_output.append([str(key), 'average', total_avg, hepex_avg, hepth_avg, Q1_avg, Q2_avg, Q3_avg, Q4_avg, xtotal_avg, xhepex_avg, xhepth_avg, xQ1_avg, xQ2_avg, xQ3_avg, xQ4_avg])
#        for x, y in val.iteritems():
#            if 'Citation logs' in x:
#                for m, n in y.iteritems():
#                    for o, p in n.iteritems():
#                        for q, r in p.iteritems():
#                            csv_placeholder = [str(key), 'year', '0', '0', '0', '0', '0', '0', '0','0', '0', '0', '0', '0', '0', '0']
#                            year = q
#                            count = r
#                            if q not in dates:
#                                count = '0'
#                            if m == 'Including self-cites':                                                 
#                                if o == 'Total':
                                    
#                                elif o == 'HEP-EX':
#                                elif o == 'HEP-TH':
#                                elif o == 'Q1':
#                                elif o == 'Q2':
#                                elif o == 'Q3':
#                                elif o == 'Q4':

#                            elif m == 'Excluding self-cites':
#                                pass
#                                if o == 'Total':
#                                elif o == 'HEP-EX':
#                                elif o == 'HEP-TH':
#                                elif o == 'Q1':
#                                elif o == 'Q2':
#                                elif o == 'Q3':
#                                elif o == 'Q4':                         
                

#        if set(dates)==1:
#            print key, set(dates)
#            csv_output.append([str(key), str(x), str(PAPERS[key]['Citation logs']['Including self-cites']['Total'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Including self-cites']['Q1'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['Q2'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Including self-cites']['Q3'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['Q4'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['Total'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q1'][dates[0]]), 
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q2'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q3'][dates[0]]),
# str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q4'][dates[0]])])

#            print([str(key), str(x), str(PAPERS[key]['Citation logs']['Including self-cites']['Total'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Including self-cites']['HEP-EX'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['HEP-TH'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Including self-cites']['Q1'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['Q2'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Including self-cites']['Q3'][dates[0]]), str(PAPERS[key]['Citation logs']['Including self-cites']['Q4'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['Total'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-EX'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['HEP-TH'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q1'][dates[0]]),
#str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q2'][dates[0]]), str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q3'][dates[0]]),
# str(PAPERS[key]['Citation logs']['Excluding self-cites']['Q4'][dates[0]])])
#        else:
#            print key, set(dates)
#            for x in range(min(dates), max(dates)+1):
#                print [key, x, PAPERS[key]['Citation logs']['Including self-cites']['Total'][x]]
#                csv_output.append([str(key), str(x), str(PAPERS[key]['Citation logs']['Including self-cites']['Total'][x])])
    
#    output_name = raw_input('Output filename: ')
#    with open(output_name, 'w') as output:
#        output.write("recid, year, total citations/year, hep-ex citations/year, hep-th citations/year, Q1 citations/year, Q2 citations/year, Q3 citations/year, Q4 citations per year, total citations/year excluding self-cites and student cites, hep-ex citations/year excluding self-cites and student cites, hep-th citations/year excluding self-cites and student cites, Q1 citations/year excluding self-cites and student cites, Q2 citations/year excluding self-cites and student cites, Q3 citations/year excluding self-cites and student cites, Q4 citations/year excluding self-cites and student cites")
#        for x in (csv_output):
#            print ','.join(x)
#            print x
#        output.write('\n'.join(','.join(csv_output)))

     


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
