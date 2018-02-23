#!/bin/bash
round=1
first_botid='0'
second_botid='1'
file='game.txt'
field='.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.'
#field='.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,.,1,0,1,1,.,.,.,0,1,0,0,.,.,.,0,1,0,0,.,.,1,1,0,1,0,1'
echo $field | egrep -q '0|1' && round=2

settings="settings player_names player0,player1
settings your_bot player$first_botid
settings timebank 10000
settings time_per_move 500
settings your_botid $first_botid
settings field_width 7
settings field_height 6"
echo "$settings" > $file
echo "update game round $round
update game field $field
action move 10000" >> $file

function new_field() {
    local inc=0
    local move=$1
    local botid=$2
    for ((i=0;i<=${#field};i=i+2)); do
        if [[ $inc%7 -eq $move ]]; then
            if [ "." == "${field:i:1}" ]; then
                pos=$inc
            else
                field=${field:0:$pos*2}$botid${field:$pos*2+1}
                break
            fi
        fi
        ((inc++))
    done
    field=${field:0:$pos*2}$botid${field:$pos*2+1}
}

function output() {
    echo "-------------------"
    echo $1 | tr ',' ' ' | sed 's/ /\n/7' | sed 's/ /\n/7' | \
        sed 's/ /\n/7' | sed 's/ /\n/7' | sed 's/ /\n/7'
    echo "-------------------"
    echo "0 1 2 3 4 5 6"
    echo
}

clear
