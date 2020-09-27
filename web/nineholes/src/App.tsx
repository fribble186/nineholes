import React from 'react';
import './App.css';
import { useState, useEffect } from 'react'
import { NineholesAI } from './ai'

interface CharacterProps {
  type: Player | null,
  is_selected: boolean,
  onClick(): void
}

enum GameStatus { start, end, waiting }
export enum Player { black, white }
export interface Character {
  type: Player | null,
  is_selected: boolean
}
export interface GameState {
  character_list: Character[][],
  player: Player | null,
  status: GameStatus,
  winner: Player | null
}

function CharacterComponent(props: CharacterProps) {
  const { type, is_selected, onClick } = props
  return type === Player.black
    ? <div className={`character_black ${is_selected ? "selected" : ""}`} onClick={onClick} />
    : type === Player.white
      ? <div className={`character_white ${is_selected ? "selected" : ""}`} onClick={onClick} />
      : <div className="character_blank" onClick={onClick} />
}

function MainStage(props: { room_id: string }) {
  let default_character_state: GameState = {
    character_list: [
      [Player.black, Player.black, Player.black].map(item => { return { type: item, is_selected: false } }),
      [null, null, null].map(item => { return { type: item, is_selected: false } }),
      [Player.white, Player.white, Player.white].map(item => { return { type: item, is_selected: false } }),
    ],
    player: Player.black,
    status: GameStatus.waiting,
    winner: null,
  }
  const [game_status, change_game_status] = useState<GameState>(default_character_state)
  const [my_role, change_my_role] = useState<Player | null>()
  const [my_websocket, set_websocket] = useState<WebSocket>()
  useEffect(() => {
    let _game_status: GameState = JSON.parse(JSON.stringify(game_status))
    if (props.room_id === "ai") {
      change_my_role(Player.black)
      _game_status.status = GameStatus.start
      change_game_status(_game_status)
    } else {
      var ws: WebSocket = new WebSocket("ws://101.133.238.228:8010/ws/" + props.room_id);
      ws.onopen = function () {
        console.log("connection start")
      }
      ws.onmessage = function (event: any) {
        console.log(event)
        if (Number(event.data) === 0) {
          change_my_role(Player.black)
        } else if (Number(event.data) === 1) {
          change_my_role(Player.white)
          _game_status.status = GameStatus.start
          ws.send(JSON.stringify({ room: props.room_id, data: _game_status }))
          change_game_status(_game_status)
        } else if (Number(event.data)) {
          change_my_role(null)
        } else {
          let data = JSON.parse(event.data)
          change_game_status(data.data)
        }
      }
      set_websocket(ws)
    }
  }, [])

  useEffect(() => {
    if (game_status.winner == null) return
    my_websocket?.close()
    let _game_status: GameState = JSON.parse(JSON.stringify(game_status))
    _game_status.status = GameStatus.end
    change_game_status(_game_status)
  }, [game_status.winner])

  const whoWin = (_game_status: GameState) => {
    let black_columns: number[] = []
    let black_rows: number[] = []
    let white_columns: number[] = []
    let white_rows: number[] = []
    _game_status.character_list.map((column: Character[], _column_index: number) => {
      column.map((cell: Character, _row_index: number) => {
        if (cell.type === Player.black) {
          black_columns.push(_column_index)
          black_rows.push(_row_index)
        } else if (cell.type === Player.white) {
          white_columns.push(_column_index)
          white_rows.push(_row_index)
        }
      })
    })
    // console.log(black_columns, black_rows, white_columns, white_rows)
    if (black_columns[0] === black_columns[1] && black_columns[1] === black_columns[2]) {
      if (black_columns[0] !== 0) return Player.black
    } else if ((black_rows[0] === black_rows[1] && black_rows[1] === black_rows[2])) {
      return Player.black
    } else if (black_columns.toString() === black_rows.toString() || black_columns.reverse().toString() === black_rows.toString()) {
      return Player.black
    }
    if (white_columns[0] === white_columns[1] && white_columns[1] === white_columns[2]) {
      if (white_columns[0] !== 2) return Player.white
    } else if ((white_rows[0] === white_rows[1] && white_rows[1] === white_rows[2])) {
      return Player.white
    } else if (white_columns.toString() === white_rows.toString() || white_columns.reverse().toString() === white_rows.toString()) {
      return Player.white
    }
    return null
  }

  const handleClick = (column_index: number, row_index: number) => {
    let _game_status: GameState = JSON.parse(JSON.stringify(game_status))
    if (_game_status.status !== GameStatus.start) return
    if (_game_status.player !== my_role) return
    let selected_indexs: { column: number, row: number } = { column: -1, row: -1 }
    let is_change = false
    _game_status.character_list.map((column: Character[], _column_index: number) => {
      column.map((cell: Character, _row_index: number) => {
        if (cell.is_selected) selected_indexs = { column: _column_index, row: _row_index }
        cell.is_selected = false
      })
    })
    if (selected_indexs.column !== -1) {
      if (_game_status.character_list[column_index][row_index].type === null) {
        if (Math.abs(column_index - selected_indexs.column) < 2 && Math.abs(row_index - selected_indexs.row) < 2) {
          let temp = _game_status.character_list[column_index][row_index]
          _game_status.character_list[column_index][row_index] = _game_status.character_list[selected_indexs.column][selected_indexs.row]
          _game_status.character_list[selected_indexs.column][selected_indexs.row] = temp
          _game_status.player = _game_status.player === Player.black ? Player.white : Player.black
          is_change = true
        }
      }
    } else {
      if (_game_status.character_list[column_index][row_index].type === _game_status.player) {
        _game_status.character_list[column_index][row_index].is_selected = true
      }
    }
    _game_status.winner = whoWin(_game_status)
    if (is_change && my_websocket) {
      my_websocket.send(JSON.stringify({ room: props.room_id, data: _game_status }))
      console.log("send success")
    } else if (is_change && props.room_id === "ai" && !_game_status.winner ) {
      let result: {last: number[], current: number[]} | null = NineholesAI(_game_status)
      let temp = _game_status.character_list[result.current[0]][result.current[1]]
      _game_status.character_list[result.current[0]][result.current[1]] = _game_status.character_list[result.last[0]][result.last[1]]
      _game_status.character_list[result.last[0]][result.last[1]] = temp
      _game_status.player = _game_status.player === Player.black ? Player.white : Player.black
      _game_status.winner = whoWin(_game_status)
    }
    change_game_status(_game_status)
  }

  return (
    <div className="flex_column">
      <div className="flex_column">
        <div className="flex_row">
          <div className={`flex_row center flex_1 ${game_status.player === Player.black ? "tomato" : ""}`}>
            <div className="character_black" />
            <div className="flex_row">
              <span>黑子</span>
              {my_role === Player.black ? (<span>（你）</span>) : null}
            </div>
          </div>
          <div className={`flex_row center flex_1 ${game_status.player === Player.white ? "tomato" : ""}`}>
            <div className="character_white" />
            <div className="flex_row">
              <span>白子</span>
              {my_role === Player.white ? (<span>（你）</span>) : null}
            </div>
          </div>
        </div>
        <div className="flex_1">
          <span>状态：{game_status.status === GameStatus.waiting ? "等待加入" : game_status.status === GameStatus.end ? "游戏结束" : "游戏中"}</span>
        </div>
        <div className="flex_1">
          <span>获胜者：{game_status.winner === Player.black ? "黑子" : game_status.winner === Player.white ? "白子" : "无"}</span>
        </div>
      </div>

      <div className="main_stage">
        <img src={require('./img/plate.png')} alt="" />
        <div className="flex_column">
          {game_status.character_list.map((column: Character[], column_index: number) => (
            <div className={`flex_row ${column_index < 2 ? "character_margin_bottom" : ""}`} key={"column" + column_index}>
              {column.map((item: Character, index: number) => (
                <div className={`${index < 2 ? "character_margin_right" : ""}`} key={"character" + index}>
                  <CharacterComponent type={item.type} is_selected={item.is_selected} onClick={() => handleClick(column_index, index)} />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

class Page extends React.Component<{ match: any }, {}>{
  componentDidMount() {
    console.log(this)
  }
  render() {
    return this.props.match ? <MainStage room_id={this.props.match.params.room_id} /> : null
  }
}

export default Page;
