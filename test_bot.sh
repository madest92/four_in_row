#!/bin/bash

function start_bot() {
    botid=$1
    [ -n "$2" ] && script='./main.py' || script='./oldmain.py'

    sed -i "s/settings your_bot .*/settings your_bot player${botid}/" $file
    sed -i "s/settings your_botid .*/settings your_botid $botid/" $file
    result=$(cat $file | $script 2>&1)
    last_move=$(echo "$result" | awk '/place_disc/{print $2}')
    field=$(tail -n2 $file | awk '/game field/{print $NF}')

    echo "Round: $round; bot $botid"
    echo "Last move: [$last_move] $field"
    echo "$result" | tail -n2

    new_field $last_move $botid
    output $field

    echo "$result" | grep -q 'WIN' && exit
    echo $field | fgrep -q '.' || exit

    echo "$settings" > $file
    echo "update game round $((round))
update game field $field
action move 10000" >> $file

}

[ -z "$1" ] && first_move_new='y' || first_move_old='y'
source settings_game.sh

while true; do
    clear
    start_bot $first_botid $first_move_new
    start_bot $second_botid $first_move_old
    ((round++))
#    sleep 2

done

#EOF
