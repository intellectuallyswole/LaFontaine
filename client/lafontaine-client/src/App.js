import logo from './logo.svg';
import './App.css';
import DragDrop from './DragDrop';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>
          File Upload to S3
        </p>
        <DragDrop />
      </header>
    </div>
  );
}

export default App;