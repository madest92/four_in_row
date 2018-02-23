#!/bin/bash
source settings_game.sh

while true; do
    ((round++))
    result=$(cat $file | ./main.py 2>&1)
    clear
    last_move=$(echo "$result" | awk '/place_disc/{print $2}')
    field=$(tail -n3 $file | awk '/game field/{print $NF}')

    echo "Round: $round"
    echo "Last move: [$last_move] $field"
    echo "$result" | tail -n2

    new_field $last_move $first_botid
    output $field
    echo "$result" | grep 'WIN' && exit

    while true; do
        echo "Enter move[0-6]: "
        read your_move
        [[ $your_move =~ ^[0-6]$ ]] && break
    done

    new_field $your_move $second_botid
    output $field

    echo "$settings" > $file
    echo "update game round $round
update game field $field
action move 10000" >> $file
done

#EOF
