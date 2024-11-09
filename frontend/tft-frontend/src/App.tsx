import './App.css';
import { useState } from 'react';

function App() {
  const [data, setData] = useState('');
  async function textCallback(text: string) {
    try {
      const searchParams = new URLSearchParams({
        query: text
      })
      const resp = await fetch('http://192.168.1.153:9000/test?' + searchParams)
      if (resp.status !== 200) {
        setData('Error')
      } else {
        const data = await resp.text()
        console.log(data)
        setData(data)
      }
    } catch(e) {
      console.log(e)
    }
  }

  return (
    <div className="App">
      Welcome to TFT QL!
      <QueryBar callback={textCallback}/>
      <SimplePrinter text={data}/>
    </div>
  );
}

interface QueryBarProps {
  callback: (text: string) => Promise<void>
}

const QueryBar: React.FC<QueryBarProps> = ({callback}) => {
  const [text, setText] = useState('');

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setText(e.target.value)
  }

  async function handleSubmit(e: React.ChangeEvent<HTMLFormElement>) {
    e.preventDefault();
    const output = text
    setText('')
    await callback(output);
  }

  return (
    <div className='QueryBar'>
      <form onSubmit={handleSubmit}>
        <input style={{width: '400px', fontFamily: 'monospace', font: 'Courier'}} value={text} onChange={handleChange}></input>
      </form>
    </div>
  )
}

interface SimplePrinterProps {
  text: string
}

const SimplePrinter: React.FC<SimplePrinterProps> = ({text}) => {
  return <textarea value={text} style={{padding: '10px', width: '100vh', height: '90vh', fontFamily: 'monospace', font: 'Courier'}}></textarea>
}

export default App;
