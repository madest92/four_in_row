#!/usr/bin/env python3
import sys
import random
from itertools import groupby

INFINITY = 99999999


class State(object):
    """ State object that extends Field and Settings.
        The AI algorithm is minimax.
        The self.settings.depth to which the search tree is expanded.
    """

    def __init__(self):
        self.settings = Settings()
        self.field = Field()
        self.round = 0

    def get_best_enumerate(self):
        """ Returns new array of numbers from the middle to the end """
        b = []
        medium = self.settings.field_width // 2
        for i in range(medium + 1):
            b.append(medium - i)
            b.append(medium + i)
        b.pop(0)
        if self.settings.field_width % 2 == 0:
            b.pop()
        return b

    def best_move(self):
        """ Returns the best move (as a column number)
            Calls minimax()
        """

        # define variables
        alpha = -INFINITY
        beta = INFINITY
        best_moves = []
        scores = {}
        states = {}
        your_botid = self.settings.your_botid
        him_botid = self.settings.him_botid
        state = self.field.field_state_90
        depth = self.settings.depth
        weight_slip = self.settings.weight_slip
        self.best_enumerate = self.get_best_enumerate()

        # check bad pos .1.1. in first line
        bad_pos = ['.', him_botid, '.', him_botid, '.']
        for i in range(self.settings.field_width):
            if i > 1 and bad_pos == self.field.field_state[-1][i - 2:i + 3]:
                return i

        # best enumerate all legal moves
        legal_moves = self.legal_moves(state, your_botid)
        for move in legal_moves:
            x = move['pos'][0]
            scores[x], states[x] = self.minimax(
                depth - 1, move['state'], move['pos'],
                your_botid, alpha, beta, []
            )
            states[x].insert(0, move['state'])

        # find best move(+/- weight_slip points)
        for move in sorted(scores, key=scores.get, reverse=True):
            if (not best_moves or
                    scores[best_moves[0]] - scores[move] <= weight_slip):
                best_moves.append(move)
        best_move = random.choice(best_moves)
        best_score = scores[best_move]

        # debug best moves
        if self.settings.debug is True:
            e("-" * 35)
            for state in states[best_move]:
                for line in reversed(list(zip(*state))):
                    e(line)
                e("")

        e(scores)
        e("Move {} - score {}\n".format(best_move, best_score))
        if best_score >= self.settings.weight_4:
            e('WIN {}'.format(self.settings.your_bot))

        return best_move

    def legal_moves(self, state, botid):
        """ Generate legal moves """

        legal_moves = []
        for x in self.best_enumerate:
            if state[x][-1] != '.':
                continue
            y = state[x].index('.')
            move = self.make_move(state, x, y, botid)
            legal_moves.append({'state': move, 'pos': [x, y]})
        return legal_moves

    def make_move(self, state, x, y, botid):
        """ Returns a copy of new state array with the added move """

        tmp = [x[:] for x in state]
        tmp[x][y] = botid
        return tmp

    def minimax(self, depth, state, positions,
                curr_botid, alpha, beta, states):
        """ Searches the tree at depth 'depth'
            Returns the alpha value
        """

        # return score if last recursion
        if depth == 0:
            return self.total_score_state(state, positions), state

        # return score*depth if gameover
        gameover = self.gameover(state, positions)
        if gameover:
            return gameover * depth, state

        # determine opponent and set default alpha
        opp_botid = self.opponent_botid(curr_botid)
        best_score = INFINITY
        if opp_botid == self.settings.your_botid:
            best_score = -INFINITY

        # get legal moves from this state
        legal_moves = self.legal_moves(state, opp_botid)
        if len(legal_moves) == 0:
            return self.total_score_state(state, positions), state

        # minimax recursive
        for move in legal_moves:
            score, futute_state = self.minimax(
                depth - 1, move['state'], move['pos'],
                opp_botid, alpha, beta, states
            )
            # max if your bot
            if opp_botid == self.settings.your_botid:
                if score > best_score:
                    best_score = score
                    futute_states = self.future_states(
                        move['state'], futute_state
                    )
                alpha = max(alpha, best_score)
            # min if him bot
            else:
                if score < best_score:
                    best_score = score
                    futute_states = self.future_states(
                        move['state'], futute_state
                    )
                beta = min(beta, best_score)
            # alpha-beta pruning
            if beta < alpha:
                break

        return best_score, futute_states

    def future_states(self, curr_state, futute_state):
        """ Combining two lists """
        if curr_state == futute_state:
            return [curr_state]

        states = []
        states.append(curr_state)

        if isinstance(futute_state, str):
            states.append(futute_state)
        else:
            states.extend(futute_state)

        return states

    def total_score_state(self, state, positions):
        """ Returns all score in state """

        max_score_won = self.settings.weight_4

        v = self.score_verticals(state, positions)
        if abs(v) >= max_score_won:
            return v

        h = self.score_horizontals(state, positions)
        if abs(h) >= max_score_won:
            return h

        g = self.score_diagonals(state, positions)
        if abs(g) >= max_score_won:
            return g

        return v + h + g

    def heuristic_score(self, your_scores, opp_scores):
        """ Simple heuristic for scoring. See settings score
        """

        s = self.settings
        # if win/lose
        if your_scores[4] > 0:
            return s.weight_4
        elif opp_scores[4] > 0:
            return -s.weight_4

        # sum score*weight
        total = your_scores[3] * s.weight_3 - opp_scores[3] * s.weight_3
        total += your_scores[2] * s.weight_2 - opp_scores[2] * s.weight_2
        # total += your_scores[1]*s.weight_1 - opp_scores[1]*s.weight_1
        return total

    def gameover(self, state, positions):
        """ Check win or lose state """

        x = positions[0]
        y = positions[1]
        width = self.settings.field_width
        height = self.settings.field_height
        score = self.settings.weight_4
        win = self.settings.combo_win
        lose = self.settings.combo_lose

        # check vertical
        vertical = ''.join(state[x][max(y - 3, 0):y + 1])
        if win == vertical:
            return score
        elif lose == vertical:
            return -score

        # check horizontal
        horizontal = [state[i][y]
                      for i in range(max(x - 3, 0), min(width, x + 4))]
        horizontal = ''.join(horizontal)
        if win in horizontal:
            return score
        elif lose in horizontal:
            return -score

        # check diagonals
        gdiagonal = ''
        bdiagonal = ''
        for i in range(max(x - 3, 0), min(width, x + 4)):
            j = x + y - i
            if 0 <= j < height:
                gdiagonal += state[i][j]
            j = y - x + i
            if 0 <= j < height:
                bdiagonal += state[i][j]
        if win in gdiagonal or win in bdiagonal:
            return score
        elif lose in gdiagonal or lose in bdiagonal:
            return -score

        return 0

    def score_verticals(self, state, positions):
        """ Returns scores in vertical """

        your_scores = [0, 0, 0, 0, 0]
        opp_scores = [0, 0, 0, 0, 0]

        # enumerate all element in state
        for x in range(self.settings.field_width):
            found_my = False
            found_opp = False
            # group element in vertical
            for item, group in groupby(reversed(state[x])):
                # break if score is exist
                if item != '.' and (found_my is True or found_opp is True):
                    break
                count = min(4, len(list(group)))
                if item == self.settings.your_botid:
                    found_my = True
                    your_scores[count] += 1
                elif item == self.settings.him_botid:
                    found_opp = True
                    opp_scores[count] += 1
            # if won return max score
            if your_scores[4] > 0:
                return self.settings.weight_4
            elif opp_scores[4] > 0:
                return -self.settings.weight_4

        return self.heuristic_score(your_scores, opp_scores)

    def score_horizontals(self, state, positions):
        """ Returns scores horizontal """

        your_scores = [0, 0, 0, 0, 0]
        opp_scores = [0, 0, 0, 0, 0]

        # enumerate all horizontal lines
        for line in zip(*state):
            line_your_scores = self.score_line(line, self.settings.your_botid)
            # return max score if win
            if line_your_scores[4] > 0:
                return self.settings.weight_4
            line_opp_scores = self.score_line(line, self.settings.him_botid)
            # return min score if lose
            if line_opp_scores[4] > 0:
                return -self.settings.weight_4
            # twice the sum of all scores
            your_scores = [x + y * 2 for x,
                           y in zip(your_scores, line_your_scores)]
            opp_scores = [x + y * 2 for x,
                          y in zip(opp_scores, line_opp_scores)]

        return self.heuristic_score(your_scores, opp_scores)

    def score_diagonals(self, state, positions):
        """ Returns scores in diagonal """

        your_scores = [0, 0, 0, 0, 0]
        opp_scores = [0, 0, 0, 0, 0]

        # get all diagonals
        width = self.settings.field_width
        height = self.settings.field_height
        min_bdiag = -width + 1
        fdiagonals = [[] for i in range(width + height - 1)]
        bdiagonals = [[] for i in range(len(fdiagonals))]
        for x in range(width):
            for y in range(height):
                fdiagonals[x + y].append(state[x][y])
                bdiagonals[y - x - min_bdiag].append(state[x][y])

        # enumerate all diagonal lines
        for line in fdiagonals + bdiagonals:
            if len(line) < 4:
                continue
            line_your_scores = self.score_line(line, self.settings.your_botid)
            # return max score if win
            if line_your_scores[4] > 0:
                return self.settings.weight_4
            line_opp_scores = self.score_line(line, self.settings.him_botid)
            # return min score if lose
            if line_opp_scores[4] > 0:
                return -self.settings.weight_4
            # twice the sum of all scores
            your_scores = [x + y * 3 for x,
                           y in zip(your_scores, line_your_scores)]
            opp_scores = [x + y * 3 for x,
                          y in zip(opp_scores, line_opp_scores)]

        return self.heuristic_score(your_scores, opp_scores)

    def score_line(self, line, curr_botid):
        """ Returns score in line """

        scores = [0, 0, 0, 0, 0]
        score = 0
        opp_botid = self.opponent_botid(curr_botid)

        # enumerate all combination in line
        for i in range(len(line) - 3):
            combination = line[i:i + 4]
            if opp_botid in combination:
                if score > 0:
                    scores[score] += 1
                score = 0
                continue
            count = combination.count(curr_botid)
            if count >= 4:
                return [0, 0, 0, 0, 1]
            score = max(score, count)
            # last combination and score > 0
            if i == len(line) - 4 and score > 0:
                scores[score] += 1

        return scores

    def opponent_botid(self, botid):
        if botid == self.settings.your_botid:
            return self.settings.him_botid
        return self.settings.your_botid


class Settings(object):
    """ Settings object contains basic game settings """

    def __init__(self):
        self.timebank = None
        self.time_per_move = None
        self.player_names = None
        self.your_bot = None
        self.your_botid = None
        self.him_botid = None
        self.field_width = None
        self.field_height = None
        self.weight_4 = 100000
        self.weight_3 = 1000
        self.weight_2 = 100
        self.weight_1 = 1
        self.weight_slip = 100
        self.depth = 4
        self.debug = False


class Field(object):
    """ Field object contains the playing field """

    def __init__(self):
        self.field_state = None
        self.field_state_reverse = None
        self.field_state_90 = None

    def update_field(self, celltypes, settings):
        """ Game field update function """

        self.field_state = [[] for _ in range(settings.field_height)]
        n_cols = settings.field_width
        for idx, cell in enumerate(celltypes):
            row_idx = idx // n_cols
            self.field_state[row_idx].append(cell)
        self.field_state_reverse = self.field_state[::-1]
        self.field_state_90 = [list(i) for i in zip(*self.field_state_reverse)]


def settings(text, state):
    """ Handle communication intended to update game settings """

    tokens = text.strip().split()[1:]
    cmd = tokens[0]
    if cmd in ('timebank', 'time_per_move', 'field_height', 'field_width'):
        # Handle setting integer settings.
        setattr(state.settings, cmd, int(tokens[1]))
    elif cmd == 'your_botid':
        your_botid = str(tokens[1])
        him_botid = str(int(not int(tokens[1])))
        setattr(state.settings, cmd, your_botid)
        setattr(state.settings, 'him_botid', him_botid)
        win = ''.join([your_botid for i in range(4)])
        lose = ''.join([him_botid for i in range(4)])
        setattr(state.settings, 'combo_win', win)
        setattr(state.settings, 'combo_lose', lose)
    elif cmd in ('your_bot',):
        # Handle setting string settings.
        setattr(state.settings, cmd, tokens[1])
    elif cmd in ('player_names',):
        # Handle setting lists of strings.
        setattr(state.settings, cmd, tokens[1:])
    else:
        raise NotImplementedError(
            'Settings command "{}" not recognized'.format(text)
        )


def update(text, state):
    """ Handle communication intended to update the game """

    tokens = text.strip().split()[2:]
    cmd = tokens[0]
    if cmd in ('round',):
        # Handle setting integer settings.
        setattr(state.settings, 'round', int(tokens[1]))
    if cmd in ('field',):
        # Handle setting the game board.
        celltypes = tokens[1].split(',')
        state.field.update_field(celltypes, state.settings)


def action(text, state):
    """ Handle communication intended to prompt the bot to take an action """

    tokens = text.strip().split()[1:]
    cmd = tokens[0]
    if cmd in ('move',):
        return make_move(state)
    else:
        raise NotImplementedError(
            'Action command "{}" not recognized'.format(text)
        )


def e(text):
    """ Debug output function """

    print(text, file=sys.stderr)


def make_move(state):
    """ Function return best move """

    # increment depth by round
    if state.settings.round == 1 and state.settings.your_botid == '0':
        return 'place_disc {}'.format(state.settings.field_width // 2)
    elif state.settings.round <= 5:
        state.settings.depth = 4
    elif state.settings.round <= 12:
        state.settings.depth = 5
    else:
        state.settings.depth = 8

    # debug board
    e("\n\n{}".format('#' * 40))
    e("\tRound {} (depth {})".format(
        state.settings.round - 1, state.settings.depth
    ))
    e("{}".format('#' * 40))
    for line in state.field.field_state:
        e(line)
    e(" ")

    return 'place_disc {}'.format(state.best_move())


def main():
    command_lookup = {'settings': settings, 'update': update, 'action': action}
    state = State()
    for input_msg in sys.stdin:
        cmd_type = input_msg.strip().split()[0]
        if 'Output' in cmd_type:
            continue
        if '#' == cmd_type[0]:
            break
        command = command_lookup[cmd_type]

        # Call the correct command.
        res = command(input_msg, state)

        # Assume if the command generates a string as output, that we need
        # to "respond" by printing it to stdout.
        if isinstance(res, str):
            print(res)
            sys.stdout.flush()


if __name__ == '__main__':
    main()
