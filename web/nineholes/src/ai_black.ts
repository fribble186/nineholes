import { GameState, Character, Player } from './App'


interface self_feasibility_dict {  // 存棋子自己的坐标和该棋子可行的坐标
  self: number[],
  feasibility: number[][]
}

interface possiblility {
  last: number[],
  current: number[]
}

export function BlackNineholesAI(currunt: GameState, isPlus: boolean = false) {
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

  function not_in_dict(loc: number[], other_blacks: self_feasibility_dict[] | null = null): boolean {  // 判断该坐标有没有棋子占用
    if (other_blacks) {
      for (let item of other_blacks) {
        if (loc.toString() === item.self.toString()) return false
      }
    } else {
      for (let item of blacks) {
        if (loc.toString() === item.self.toString()) return false
      }
    }
    for (let item of whites) {
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
  console.log(1)
  // 必胜，登龙剑，处理下一步必胜的走法
  for (let index = 0; index < 3; index++) {
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

      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {  // 判断是否胜利
        if (next_step[0] !== 0) return { last: blacks[index].self, current: next_step }
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        return { last: blacks[index].self, current: next_step }
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length === 3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
          return { last: blacks[index].self, current: next_step }
      }
    }
  }
  console.log(2)
  // 你先走，小杜
  let white_wins: number[][] = []
  for (let index = 0; index < 3; index++) {  // 获取白子下一步就能获胜的坐标
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
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 0) white_wins.push(next_step)
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        white_wins.push(next_step)
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length === 3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
          white_wins.push(next_step)
      }
    }
  }
  for (let white_win of white_wins) {  // 去找可以去堵住的黑子
    for (let index = 0; index < 3; index++) {
      let item = blacks[index]
      for (let feasibility of item.feasibility) {
        if (white_win.toString() === feasibility.toString()) {
          return { last: blacks[index].self, current: feasibility }
        }
      }
    }
  }
  console.log(3)
  // 能堵就堵
  // let white_maybe_wins: number[][] = []
  // for (let index = 0; index < 3; index++) {
  //   let item = whites[index]
  //   let other_1: number[]
  //   let other_2: number[]
  //   if (index === 0) {
  //     other_1 = whites[1].self
  //     other_2 = whites[2].self
  //   } else if (index === 1) {
  //     other_1 = whites[0].self
  //     other_2 = whites[2].self
  //   } else {
  //     other_1 = whites[0].self
  //     other_2 = whites[1].self
  //   }
  //   if (other_1[0] === other_2[0]) {
  //     if (Math.abs((other_1[1] - other_2[1])) === 0) white_maybe_wins.push([other_1[0], 1])
  //   } else if (other_1[1] === other_2[1]) {
  //     if (Math.abs((other_1[1] - other_2[1])) === 0) white_maybe_wins.push([1, other_1[1]])
  //   } else if ((Math.abs(other_1[0] - other_2[0]) === 0) && (Math.abs(other_1[1] - other_2[1]) === 0)) {
  //     white_maybe_wins.push([1, 1])
  //   }
  // }
  // if (white_maybe_wins.length === 1) {
  //   for (let white_win of white_maybe_wins) {  // 去找可以去堵住的黑子
  //     for (let index = 0; index < 3; index++) {
  //       let item = blacks[index]
  //       for (let feasibility of item.feasibility) {
  //         if (white_win.toString() === feasibility.toString()) {
  //           return { last: blacks[index].self, current: feasibility }
  //         }
  //       }
  //     }
  //   }
  // }

  // 暂停一下
  function lose_if_left(next_step: number[]): boolean {  // 如果黑子走了，该占位能使白子赢
    for (let index = 0; index < 3; index++) {
      let other_1: number[]
      let other_2: number[]
      let i_can_win: boolean = false
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
      if (next_step[0] === other_1[0] && other_1[0] === other_2[0]) {
        if (next_step[0] !== 2) i_can_win = true
      } else if (next_step[1] === other_1[1] && other_1[1] === other_2[1]) {
        i_can_win = true
      } else if (columns.sort().toString() === rows.sort().toString()) {
        if ((Array.from(new Set(columns)).length === 3) && (Math.abs(next_step[0] - next_step[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
          i_can_win = true
      }
      if (i_can_win) {
        if (Math.abs(next_step[0] - whites[index].self[0]) == 2) {
          i_can_win = false
        } else if (Math.abs(next_step[1] - whites[index].self[1]) == 2) {
          i_can_win = false
        } else if ((Math.abs(whites[index].self[0] - whites[index].self[1]) === 1) && (Math.abs(next_step[0] - next_step[1]) === 1)) {
          i_can_win = false
        }
      }
      if (i_can_win) return true
    }
    return false
  }

  function get_free_character(curindex: number, current: number[]): number {  // 获取可动的黑棋棋子数量
    let _blacks: self_feasibility_dict[] = JSON.parse(JSON.stringify(blacks))
    _blacks[curindex].self = current
    for (let item of _blacks) {
      item.feasibility = []
      let new_column: number = 0
      let new_row: number = 0

      new_column = item.self[0] + 1
      if (new_column <= 2 && not_in_dict([new_column, item.self[1]], _blacks)) item.feasibility.push([new_column, item.self[1]])
      new_column = item.self[0] - 1
      if (new_column >= 0 && not_in_dict([new_column, item.self[1]], _blacks)) item.feasibility.push([new_column, item.self[1]])
      new_row = item.self[1] + 1
      if (new_row <= 2 && not_in_dict([item.self[0], new_row], _blacks)) item.feasibility.push([item.self[0], new_row])
      new_row = item.self[1] - 1
      if (new_row >= 0 && not_in_dict([item.self[0], new_row], _blacks)) item.feasibility.push([item.self[0], new_row])

      if (Math.abs(item.self[0] - item.self[1]) !== 1) {
        new_column = item.self[0] + 1; new_row = item.self[1] + 1
        if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] - 1
        if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] + 1; new_row = item.self[1] - 1
        if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] + 1
        if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
      }
    }
    let free_character_num = 0
    for (let item of _blacks) {
      if (item.feasibility.length) free_character_num++
    }
    return free_character_num
  }

  // 下一步就会被白子包围或白子赢了，可动棋子为1，导致输的场面
  function next_step_lose_if_left(curindex: number, current: number[]): boolean {  // !CAUTION: whites经过这个方法已经改变了
    let _blacks: self_feasibility_dict[] = JSON.parse(JSON.stringify(blacks))
    _blacks[curindex].self = current
    let _whites = JSON.parse(JSON.stringify(whites))
    let i_can_win: boolean = false
    for (let item of whites) {
      let new_column: number = 0
      let new_row: number = 0
      item.feasibility = []
      new_column = item.self[0] + 1
      if (new_column <= 2 && not_in_dict([new_column, item.self[1]], _blacks)) item.feasibility.push([new_column, item.self[1]])
      new_column = item.self[0] - 1
      if (new_column >= 0 && not_in_dict([new_column, item.self[1]], _blacks)) item.feasibility.push([new_column, item.self[1]])
      new_row = item.self[1] + 1
      if (new_row <= 2 && not_in_dict([item.self[0], new_row], _blacks)) item.feasibility.push([item.self[0], new_row])
      new_row = item.self[1] - 1
      if (new_row >= 0 && not_in_dict([item.self[0], new_row], _blacks)) item.feasibility.push([item.self[0], new_row])

      if (Math.abs(item.self[0] - item.self[1]) !== 1) {
        new_column = item.self[0] + 1; new_row = item.self[1] + 1
        if (new_column <= 2 && new_row <= 2 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] - 1
        if (new_column >= 0 && new_row >= 0 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] + 1; new_row = item.self[1] - 1
        if (new_column <= 2 && new_row >= 0 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
        new_column = item.self[0] - 1; new_row = item.self[1] + 1
        if (new_column >= 0 && new_row <= 2 && not_in_dict([new_column, new_row], _blacks)) item.feasibility.push([new_column, new_row])
      }
    }
    for (let index = 0; index < 3; index++) {
      let other_1: number[]
      let other_2: number[]
      if (index === 0) {
        other_1 = _whites[1].self
        other_2 = _whites[2].self
      } else if (index === 1) {
        other_1 = _whites[0].self
        other_2 = _whites[2].self
      } else {
        other_1 = _whites[0].self
        other_2 = _whites[1].self
      }
      for (let feasibility of whites[index].feasibility) {
        whites[index].self = feasibility
        let columns: number[] = [whites[index].self[0], other_1[0], other_2[0]]
        let rows: number[] = [whites[index].self[1], other_1[1], other_2[1]]
        if (whites[index].self[0] === other_1[0] && other_1[0] === other_2[0]) {
          if (whites[index].self[0] !== 0) i_can_win = true
        } else if (whites[index].self[1] === other_1[1] && other_1[1] === other_2[1]) {
          i_can_win = true
        } else if (columns.sort().toString() === rows.sort().toString()) {
          if ((Array.from(new Set(columns)).length === 3) && (Math.abs(whites[index].self[0] - whites[index].self[1]) !== 1) && (Math.abs(other_1[0] - other_1[1]) !== 1) && (Math.abs(other_2[0] - other_2[1]) !== 1))
            i_can_win = true
        }
        console.log(whites, other_1, other_2)
        if (!i_can_win && get_free_character(curindex, current) === 1) {
          if (other_1[0] === other_2[0] || other_1[1] === other_2[1]) {
            i_can_win = true
          } else if ((Math.abs(other_1[0] - other_2[0]) === 1) && (Math.abs(other_1[1] - other_2[1]) === 1)) {
            i_can_win = true
          } else {
            i_can_win = false
          }
        }
      }
    }
    whites = _whites
    return i_can_win
  }

  // 拔刀
  console.log(blacks, whites)
  if (whites[0].self[0] === 2 && whites[1].self[0] === 2 && whites[2].self[0] === 2) {
    console.log("拔刀")
    if ((blacks[0].self[0] === blacks[1].self[0]) && (blacks[2].self[0] === blacks[1].self[0])) {
      blacks[0].feasibility = blacks[0].feasibility.filter(item => (item[0] !== 1 || item[1] !== 1))
      blacks[2].feasibility = blacks[2].feasibility.filter(item => (item[0] !== 1 || item[1] !== 1))
    }
  }

  // 众里寻他千百度，慕然回首，那人却在循环最深处
  let possible_list: possiblility[] = []
  for (let index = 0; index < 3; index++) {
    if (blacks[index].feasibility.length) {
      if (lose_if_left(blacks[index].self)) {
        console.log("这一步让了我就输了" + blacks[index].self)
        continue
      }
      for (let f_random = 0; f_random < blacks[index].feasibility.length; f_random++) {
        // if (get_free_character(f_random, blacks[index].feasibility[f_random]) === 1) {
        //   console.log("这一步下去我会走投无路" + blacks[index].self + "," + blacks[index].feasibility[f_random])
        //   continue
        // }
        // if (next_step_lose_if_left(index, blacks[index].feasibility[f_random])) {
        //   console.log("这一步下去黑子再走一步我会走投无路" + blacks[index].self + "," + blacks[index].feasibility[f_random])
        //   continue
        // }

        possible_list.push({ last: blacks[index].self, current: blacks[index].feasibility[f_random] })
      }
    }
  }
  console.log(possible_list)
  if (isPlus) {
    if (possible_list.length > 1) {
      return null
    }
  }
  if (possible_list.length) {

    let random: number = parseInt((Math.random() * possible_list.length).toString())
    console.log(random)
    return possible_list[random]
  }
  // 绝望desperate
  for (let index = 0; index < 3; index++) {
    if (blacks[index].feasibility.length) {
      if (lose_if_left(blacks[index].self)) continue
      let f_random: number = parseInt((Math.random() * blacks[index].feasibility.length).toString())
      return { last: blacks[index].self, current: blacks[index].feasibility[f_random] }
    }
  }
  for (let index = 0; index < 3; index++) {
    if (blacks[index].feasibility.length) {
      let f_random: number = parseInt((Math.random() * blacks[index].feasibility.length).toString())
      return { last: blacks[index].self, current: blacks[index].feasibility[f_random] }
    }
  }

  return null
}