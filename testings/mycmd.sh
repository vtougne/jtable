#!/bin/bash

# Fonction de complétion
_mycmd_completion() {
    local cur prev opts
    cur="${COMP_WORDS[COMP_CWORD]}"    # Mot en cours de complétion
    prev="${COMP_WORDS[COMP_CWORD-1]}" # Mot précédent

    opts="start stop"

    # Si c'est le premier argument, on propose les options
    if [[ ${COMP_CWORD} == 1 ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    fi
}

# Enregistrer la fonction de complétion pour la commande `mycmd`
complete -F _mycmd_completion mycmd
