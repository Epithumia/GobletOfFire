# -*- coding: utf-8 -*-

import argparse

from cylp.cy import CyClpSimplex
from cylp.py.modeling.CyLPModel import CyLPArray
from sqlalchemy import create_engine

from models import (
    DBSession,
    Etudiant,
    Parcours,
    Voeu
)
from special import special


def tournament(args):
    # Configuration
    engine = create_engine('sqlite:///etudiants.sqlite', echo=False)
    DBSession.configure(bind=engine)

    # On récupere les donnes de la BDD
    students = DBSession.query(Etudiant).filter(Etudiant.enseignant.is_(None))
    nb_students = DBSession.query(Etudiant).filter(
        Etudiant.enseignant.is_(None)).count()
    nb_parcours = DBSession.query(Parcours).count()

    # Capacité des groupes
    capa_min_pec = 14
    capa_max_pec = 15
    capa_min_pel = 14
    capa_max_pel = 16

    # On construit le modèle
    barre_min = args.b
    model = CyClpSimplex()
    x = []
    s_list = {}
    for s in students.all():
        v = model.addVariable('etu' + str(s.id), nb_parcours, isInt=True)
        x.append(v)

    z = 0.0
    i = 0
    for s in students.all():
        reorder = False
        s_list[str(i)] = s.id
        voeux = DBSession.query(Voeu).filter(
            Voeu.idEtudiant == s.id).order_by(Voeu.idParcours).all()
        s_voeux = []
        rang_q = voeux[nb_parcours - 1].rang
        if rang_q != nb_parcours and rang_q != -1:
            if s.nom not in special or 'quebec' not in special[s.nom]:
                reorder = True
            else:
                reorder = not special[s.nom]['quebec']
        for v in voeux:
            if v.rang == -1:
                score = 0
            else:
                if reorder and v.rang > rang_q:
                    rang = v.rang - 1
                elif reorder and v.rang == rang_q:
                    rang = 9
                else:
                    rang = v.rang
                malus = 0.0
                if s.malus > 0:
                    malus += s.malus
                if s.absences is not None:
                    malus += float(s.absences) / 15
                score = 2.0 ** (rang - malus)
            s_voeux.append(score)
        a = CyLPArray(s_voeux)
        b = CyLPArray([1.0 for j in range(nb_parcours)])
        z += a * x[i]
        model += b * x[i] >= 1
        model += b * x[i] <= 1
        model += x[i] >= 0
        model += x[i] <= 1
        i += 1
    model.objective = z

    # Taille des groupes MpInge (PEL)
    for j in [0, 3, 6]:  # Attention, dans la BDD, le parcours vont de 1 à 8 -> décalage de 1
        c = 0
        for i in range(nb_students):
            c += x[i][j]
        model += c <= capa_max_pel
        model += c >= capa_min_pel

    # Taille des groupes PEC
    for j in [1, 2, 4, 5, 7]:
        c = 0
        for i in range(nb_students):
            c += x[i][j]
        model += c <= capa_max_pec
        model += c >= capa_min_pec

    # Etudiants trop bas en maths
    i = 0
    for s in students.all():
        if s.moyenneMaths is not None and s.moyenneMaths < barre_min:
            model += x[i][0] + x[i][3] + x[i][6] == 0
        i += 1

    # Québec
    i = 0
    for s in students.all():
        if s.nom not in special or 'quebec' not in special[s.nom]:
            model += x[i][nb_parcours - 1] == 0
        i += 1

    # Cas particuliers (cf special.py)
    i = 0
    for s in students.all():
        if s.nom in special and 'force' in special[s.nom]:
            for cas in special[s.nom]['force']:
                if not special[s.nom]['force'][cas]:
                    model += x[i][int(cas) - 1] == 0
        i += 1

    cbc_model = model.getCbcModel()
    cbc_model.logLevel = 0
    cbc_model.branchAndBound()

    if cbc_model.isRelaxationOptimal() and args.v:
        for s in students.all():
            r = cbc_model.primalVariableSolution['etu' + str(s.id)]
            print s.nom + '|',
            j = 1
            reorder = False
            for res in r:
                if res == 1:
                    if j == 1 or j == 4 or j == 7:
                        print "!",
                    par = DBSession.query(Parcours).filter(
                        Parcours.id == j).one()
                    print par.nom,
                    voeux = DBSession.query(Voeu).filter(
                        Voeu.idEtudiant == s.id).order_by(Voeu.idParcours).all()
                    rang_q = voeux[nb_parcours - 1].rang
                    if rang_q != nb_parcours and rang_q != -1:
                        if s.nom not in special or 'quebec' not in special[s.nom]:
                            reorder = True
                        else:
                            reorder = not special[s.nom]['quebec']
                    son_voeu = DBSession.query(Voeu).filter(
                        Voeu.idEtudiant == s.id).filter(Voeu.idParcours == j).one()
                    if reorder and son_voeu.rang == rang_q:
                        rang = 9
                    elif reorder and son_voeu.rang > rang_q:
                        rang = son_voeu.rang - 1
                    else:
                        rang = son_voeu.rang
                    print '|' + str(rang) + '',
                    print '|' + str(s.moyenneMaths),
                    print '|' + str(s.absences),
                    if reorder:
                        print '|*'
                    else:
                        print '|'
                j += 1

    nb_stu_grp = [0 for n in range(nb_parcours)]
    rangs_stu = [0 for n in range(nb_parcours)]
    indecis = 0
    pec2pel = 0
    pel2pec = 0

    if cbc_model.isRelaxationOptimal() and (args.s or args.csv):
        for s in students.all():
            r = cbc_model.primalVariableSolution['etu' + str(s.id)]
            j = 1
            reorder = False
            for res in r:
                if res == 1:
                    nb_stu_grp[j - 1] += 1
                    voeux = DBSession.query(Voeu).filter(
                        Voeu.idEtudiant == s.id).order_by(Voeu.idParcours).all()
                    rang_q = voeux[nb_parcours - 1].rang
                    if rang_q != nb_parcours and rang_q != -1:
                        if s.nom not in special or 'quebec' not in special[s.nom]:
                            reorder = True
                        else:
                            reorder = not special[s.nom]['quebec']
                    son_voeu = DBSession.query(Voeu).filter(
                        Voeu.idEtudiant == s.id).filter(Voeu.idParcours == j).one()
                    if reorder and son_voeu.rang == rang_q:
                        rang = 9
                    elif reorder and son_voeu.rang > rang_q:
                        rang = son_voeu.rang - 1
                    else:
                        rang = son_voeu.rang
                    if rang != -1:
                        rangs_stu[rang - 1] += 1
                        son_voeu_un = DBSession.query(Voeu).filter(
                            Voeu.idEtudiant == s.id).filter(Voeu.rang == 1).one()
                        if son_voeu_un.idParcours in [1, 4, 7] and son_voeu.idParcours not in [1, 4, 7]:
                            pel2pec += 1
                        elif son_voeu_un.idParcours not in [1, 4, 7] and son_voeu.idParcours in [1, 4, 7]:
                            pec2pel += 1
                    else:
                        indecis += 1
                j += 1

        if args.s:
            print "Etudiants par groupe : ", nb_stu_grp
            print "Etudiants par rang de voeu : ", rangs_stu
            print "Passages PEC->PEL", pec2pel
            print "Passage PEL->PEC", pel2pec
            print "Indécis : ", indecis

        if args.csv:
            print barre_min, ",",
            for item in nb_stu_grp:
                print item, ",",
            for item in rangs_stu:
                print item, ",",
            print pec2pel, ",", pel2pec

    if cbc_model.isRelaxationInfeasible():
        print "Pas de solution possible"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Répartir les etudiants dans les parcours.')
    parser.add_argument('-b', default=10, type=float, metavar='barre_minimum',
                        help='Barre minimum à avoir pour acceder à MpInge')
    parser.add_argument(
        '-v', action='store_true', help='Afficher les assignations')
    parser.add_argument(
        '-s', action='store_true', help='Afficher des statistiques')
    parser.add_argument(
        '-csv', action='store_true', help='Afficher des statistiques en csv')
    args = parser.parse_args()
    tournament(args)
