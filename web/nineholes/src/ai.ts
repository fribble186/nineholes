import { GameState, Character, Player } from './App'


interface self_feasibility_dict {  // 存棋子自己的坐标和该棋子可行的坐标
  self: number[],
  feasibility: number[][]
}

export function NineholesAI(currunt: GameState) {
  let character_list: Character[][] = currunt.character_list
  let blacks: self_feasibility_dict[] = []
  let whites: self_feasibility_dict[] = []
  character_list.forEach((column: Character[], column_index: number) => {  // 先获取黑子和白子自己的坐标
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

  function not_in_dict(loc: number[], other_whites: self_feasibility_dict[] | null = null): boolean {  // 判断该坐标有没有棋子占用
    if (other_whites) {
      for (let item of other_whites) {
        if (loc.toString() === item.self.toString()) return false
      }
    } else {
      for (let item of whites) {
        if (loc.toString() === item.self.toString()) return false
      }
    }
    for (let item of blacks) {
      if (loc.toString() === item.self.toString()) return false
    }
    return true
  }

  for (let item of blacks) {  // 获取所有黑子可行的坐标
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

    if (Math.abs(item.self[0] - item.self[1]) !== 1) {  // 如果坐标之差不等于1则可以斜着走
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

  for (let item of whites) {  // 获取所有白子可行的坐标
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
  for (let index = 0; index < 3; index++) {
    let item = whites[index]
    for (let next_step of item.feasibility) {
      let other_1: number[]
      let other_2: number[]
      if (index === 0) {
        other_1 = whites[1].self
        other_2 = whites[2].self
      } else if (index === 1) {
        other_1 = whites[0].self
        other_2 = whites[2].self
      } else {
        other_1 = whites[0].self
        other_2 = whites[1].self
      }
      let columns: number[] = [next_step[0], other_1[0], other_2[0]]
      let rows: number[] = [next_step[1], other_1[1], other_2[1]]

      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {  // 判断是否胜利
        if (next_step[0] !== 2) return { last: whites[index].self, current: next_step }
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        return { last: whites[index].self, current: next_step }
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length===3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
        return { last: whites[index].self, current: next_step }
      }
    }
  }

  // 你先走，小杜
  let black_wins: number[][] = []
  for (let index = 0; index < 3; index++) {  // 获取黑子下一步就能获胜的坐标
    let item = blacks[index]
    for (let next_step of item.feasibility) {
      let other_1: number[]
      let other_2: number[]
      if (index === 0) {
        other_1 = blacks[1].self
        other_2 = blacks[2].self
      } else if (index === 1) {
        other_1 = blacks[0].self
        other_2 = blacks[2].self
      } else {
        other_1 = blacks[0].self
        other_2 = blacks[1].self
      }
      let columns: number[] = [next_step[0], other_1[0], other_2[0]]
      let rows: number[] = [next_step[1], other_1[1], other_2[1]]
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 0) black_wins.push(next_step)
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        black_wins.push(next_step)
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length===3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
        black_wins.push(next_step)
      }
    }
  }
  for (let black_win of black_wins) {  // 去找可以去堵住的白子
    for (let index = 0; index < 3; index++) {
      let item = whites[index]
      for (let feasibility of item.feasibility) {
        if (black_win.toString() === feasibility.toString()) {
          return { last: whites[index].self, current: feasibility }
        }
      }
    }
  }

  // 暂停一下
  function lose_if_left(next_step: number[]): boolean {  // 如果白子走了，该占位能使黑子赢
    for (let index = 0; index < 3; index++) {
      let other_1: number[]
      let other_2: number[]
      let i_can_win: boolean = false
      if (index === 0) {
        other_1 = blacks[1].self
        other_2 = blacks[2].self
      } else if (index === 1) {
        other_1 = blacks[0].self
        other_2 = blacks[2].self
      } else {
        other_1 = blacks[0].self
        other_2 = blacks[1].self
      }
      let columns: number[] = [next_step[0], other_1[0], other_2[0]]
      let rows: number[] = [next_step[1], other_1[1], other_2[1]]
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 0) i_can_win = true
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        i_can_win = true
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length===3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
        i_can_win = true
      }
      if (i_can_win) {
        if ((next_step[0] - blacks[index].self[0]) == 2) {
          i_can_win = false
        } else if ((next_step[1] - blacks[index].self[1]) == 2) {
          i_can_win = false
        } else if ((Math.abs(blacks[index].self[0] - blacks[index].self[1]) === 1) && (Math.abs(next_step[0] - next_step[1]) === 1)) {
          i_can_win = false
        }
      }
      if (i_can_win) return true
    }
    return false
  }

  function get_free_character(curindex: number, current: number[]): number {  // 获取可动的白棋棋子数量
    let _whites: self_feasibility_dict[] = JSON.parse(JSON.stringify(whites))
    _whites[curindex].self = current
    for (let item of _whites) {
      item.feasibility = []
      let new_column: number = 0
      let new_row: number = 0

      new_column = item.self[0] + 1
      if (new_column <= 2 && not_in_dict([new_column, item.self[1]], _whites)) item.feasibility.push([new_column, item.self[1]])
      new_column = item.self[0] - 1
      if (new_column >= 0 && not_in_dict([new_column, item.self[1]], _whites)) item.feasibility.push([new_column, item.self[1]])
      new_row = item.self[1] + 1
      if (new_row <= 2 && not_in_dict([item.self[0], new_row], _whites)) item.feasibility.push([item.self[0], new_row])
      new_row = item.self[1] - 1
      if (new_row >= 0 && not_in_dict([item.self[0], new_row], _whites)) item.feasibility.push([item.self[0], new_row])

      if (Math.abs(item.self[0] - item.self[1]) !== 1) {
        new_column = item.self[0] + 1; new_row = item.self[1] + 1
        if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] - 1
        if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] + 1; new_row = item.self[1] - 1
        if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] + 1
        if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
      }
    }
    let free_character_num = 0
    for (let item of _whites) {
      if (item.feasibility.length) free_character_num++
    }
    return free_character_num
  }

  // 下一步就会被黑子包围，可动棋子为1，导致输的场面
  function next_step_lose_if_left(curindex: number, current: number[]): boolean {  // !CAUTION: blacks经过这个方法已经改变了
    let _whites: self_feasibility_dict[] = JSON.parse(JSON.stringify(whites))
    _whites[curindex].self = current
    let _blacks = JSON.parse(JSON.stringify(blacks))
    let i_can_win: boolean = false
    for (let item of blacks) {
      let new_column: number = 0
      let new_row: number = 0
      item.feasibility = []
      new_column = item.self[0] + 1
      if (new_column <= 2 && not_in_dict([new_column, item.self[1]], _whites)) item.feasibility.push([new_column, item.self[1]])
      new_column = item.self[0] - 1
      if (new_column >= 0 && not_in_dict([new_column, item.self[1]], _whites)) item.feasibility.push([new_column, item.self[1]])
      new_row = item.self[1] + 1
      if (new_row <= 2 && not_in_dict([item.self[0], new_row], _whites)) item.feasibility.push([item.self[0], new_row])
      new_row = item.self[1] - 1
      if (new_row >= 0 && not_in_dict([item.self[0], new_row], _whites)) item.feasibility.push([item.self[0], new_row])

      if (Math.abs(item.self[0] - item.self[1]) !== 1) {
        new_column = item.self[0] + 1; new_row = item.self[1] + 1
        if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] - 1
        if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] + 1; new_row = item.self[1] - 1
        if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] + 1
        if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row], _whites)) item.feasibility.push([new_column, new_row])
      }
    }
    for (let index = 0; index < 3; index++) {
      for (let feasibility of blacks[index].feasibility) {
        blacks[index].self = feasibility
        console.log(get_free_character(curindex, current))
        if (get_free_character(curindex, current) === 1) i_can_win = true
      }
    }
    blacks = _blacks
    return i_can_win
  }

  // suit yourself
  for (let index = 0; index < 100; index++) {  // 随你走，但是如果找不到赢的坐标则退出循环
    let random: number = parseInt((Math.random() * 3).toString())
    if (whites[random].feasibility.length) {
      if (lose_if_left(whites[random].self)) continue
      let f_random: number = parseInt((Math.random() * whites[random].feasibility.length).toString())
      if (get_free_character(random, whites[random].feasibility[f_random]) === 1) continue
      if (next_step_lose_if_left(random, whites[random].feasibility[f_random])) continue
      return { last: whites[random].self, current: whites[random].feasibility[f_random] }
    }
  }

  // desperate
  for (let index=0;index<3;index++) {
    if (whites[index].feasibility.length) {
      if (lose_if_left(whites[index].self)) continue
      let f_random: number = parseInt((Math.random() * whites[index].feasibility.length).toString())
      return { last: whites[index].self, current: whites[index].feasibility[f_random] }
    }
  }
  
  return null
}