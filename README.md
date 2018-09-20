Goblet Of Fire
--------------

Application pour l'affectation d'étudiants en groupes/parcours en fonction de critères de moyenne de maths, d'assiduité et de leurs voeux ordonnés.

Nécessite Vagrant (et une connexion internet pour s'installer).

Instructions d'installation une fois Vagrant installé et configuré :

    git clone https://git.airelle.info/airelle/GobletOfFire.git GobletOfFire
    cd GobletOfFire
    vagrant up

Cela va prendre un peu de temps, un fois terminé :

    vagrant ssh

Puis une fois dans la machine virtuelle :

    ./run.sh
    
Cf le script run.sh pour voir la commande utilisée pour lancer le script. Le programme tournament.py prend les options suivantes :

    -h, --help        show this help message and exit
    -b barre_minimum  Barre minimum à avoir pour acceder à MpInge
    -v                Afficher les assignations
    -s                Afficher des statistiques
    -csv              Afficher des statistiques en csv
    
La base de données est stockée dans `etudiants.sqlite` qui se trouve dans le sous-dossier projets/TriWizard et est déjà remplie d'étudiants fictifs et un enseignant.
