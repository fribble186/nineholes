import { GameState, Character, Player } from './App'


interface self_feasibility_dict {
  self: number[],
  feasibility: number[][]
}

export function NineholesAI(currunt: GameState) {
  let character_list: Character[][] = currunt.character_list
  let blacks: self_feasibility_dict[] = []
  let whites: self_feasibility_dict[] = []
  character_list.forEach((column: Character[], column_index: number) => {
    column.forEach((cell: Character, row_index: number) => {
      let character: self_feasibility_dict
      if (cell.type !== null) {
        character = {
          self: [column_index, row_index],
          feasibility: []
        }
        if (cell.type === Player.black) blacks.push(character)
        else if (cell.type === Player.white) whites.push(character)
      }
    })
  })

  function not_in_dict(loc: number[]): boolean {
    for (let item of blacks) {
      if (loc.toString() === item.self.toString()) return false
    }
    for (let item of whites) {
      if (loc.toString() === item.self.toString()) return false
    }
    return true
  }

  for (let item of blacks) {
    let new_column: number = 0
    let new_row: number = 0

    new_column = item.self[0] + 1
    if (new_column <= 2 && not_in_dict([new_column, item.self[1]])) item.feasibility.push([new_column, item.self[1]])
    new_column = item.self[0] - 1
    if (new_column >= 0 && not_in_dict([new_column, item.self[1]])) item.feasibility.push([new_column, item.self[1]])
    new_row = item.self[1] + 1
    if (new_row <= 2 && not_in_dict([item.self[0], new_row])) item.feasibility.push([item.self[0], new_row])
    new_row = item.self[1] - 1
    if (new_row >= 0 && not_in_dict([item.self[0], new_row])) item.feasibility.push([item.self[0], new_row])

    if (Math.abs(item.self[0] - item.self[1]) !== 1) {
      new_column = item.self[0] + 1; new_row = item.self[1] + 1
      if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] - 1; new_row = item.self[1] - 1
      if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] + 1; new_row = item.self[1] - 1
      if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] - 1; new_row = item.self[1] + 1
      if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
    }
  }

  for (let item of whites) {
    let new_column: number = 0
    let new_row: number = 0

    new_column = item.self[0] + 1
    if (new_column <= 2 && not_in_dict([new_column, item.self[1]])) item.feasibility.push([new_column, item.self[1]])
    new_column = item.self[0] - 1
    if (new_column >= 0 && not_in_dict([new_column, item.self[1]])) item.feasibility.push([new_column, item.self[1]])
    new_row = item.self[1] + 1
    if (new_row <= 2 && not_in_dict([item.self[0], new_row])) item.feasibility.push([item.self[0], new_row])
    new_row = item.self[1] - 1
    if (new_row >= 0 && not_in_dict([item.self[0], new_row])) item.feasibility.push([item.self[0], new_row])

    if (Math.abs(item.self[0] - item.self[1]) !== 1) {
      new_column = item.self[0] + 1; new_row = item.self[1] + 1
      if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] - 1; new_row = item.self[1] - 1
      if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] + 1; new_row = item.self[1] - 1
      if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
      new_column = item.self[0] - 1; new_row = item.self[1] + 1
      if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row])) item.feasibility.push([new_column, new_row])
    }
  }

  // 必胜，登龙剑，处理下一步必胜的走法
  whites.forEach((item: self_feasibility_dict, index: number) => {
    for (let next_step of item.feasibility) {
      let other_1: number[]
      let other_2: number[]
      if (index === 0 ) {
        other_1 = whites[1].self
        other_2 = whites[2].self
      } else if (index === 1){
        other_1 = whites[0].self
        other_2 = whites[2].self
      } else{
        other_1 = whites[0].self
        other_2 = whites[1].self
      }
      let columns: number[] = [next_step[0], other_1[0], other_2[0]]
      let rows: number[] = [next_step[1], other_1[1], other_2[1]]
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 2) return {last: whites[index].self,current: next_step}
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        return {last: whites[index].self,current: next_step}
      } else if (columns.sort().toString() === rows.sort().toString()) {
        return {last: whites[index].self,current: next_step}
      }
    }
  })

  // 你先走，小杜
  let black_wins: number[][] = []
  blacks.forEach((item: self_feasibility_dict, index: number) => {
    for (let next_step of item.feasibility) {
      let other_1: number[]
      let other_2: number[]
      if (index === 0 ) {
        other_1 = blacks[1].self
        other_2 = blacks[2].self
      } else if (index === 1){
        other_1 = blacks[0].self
        other_2 = blacks[2].self
      } else{
        other_1 = blacks[0].self
        other_2 = blacks[1].self
      }
      let columns: number[] = [next_step[0], other_1[0], other_2[0]]
      let rows: number[] = [next_step[1], other_1[1], other_2[1]]
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 2) black_wins.push(next_step)
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        return black_wins.push(next_step)
      } else if (columns.toString() === rows.toString() || columns.reverse().toString() === rows.toString()) {
        return black_wins.push(next_step)
      }
    }
  })
  for (let black_win of black_wins) {
    whites.forEach((item: self_feasibility_dict, index: number)=> {
      for (let feasibility of item.feasibility) {
        if (black_win.toString() === feasibility.toString()) {
          return {last: whites[index].self, current: feasibility}
        }
      }
    })
  }

  // suit yourself
  while (true){
    let random: number = parseInt((Math.random() * 3).toString())
    if (whites[random].feasibility.length) {
      let f_random: number = parseInt((Math.random() * whites[random].feasibility.length).toString())
      return {last: whites[random].self, current: whites[random].feasibility[f_random]}
    }
  }
}