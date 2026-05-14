import { useState, useCallback, useEffect } from 'react';

export default function FileLoader({ onDataLoaded }) {
  const [dragOver1, setDragOver1] = useState(false);
  const [dragOver2, setDragOver2] = useState(false);
  const [error1, setError1] = useState(null);
  const [error2, setError2] = useState(null);
  const [fileName1, setFileName1] = useState(null);
  const [fileName2, setFileName2] = useState(null);
  const [data1, setData1] = useState(null);
  const [data2, setData2] = useState(null);

  useEffect(() => {
    onDataLoaded([data1, data2]);
  }, [data1, data2, onDataLoaded]);

  const parseAndLoad = useCallback(
    (file, setter, nameSetter, errorSetter) => {
      errorSetter(null);
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const result = JSON.parse(e.target.result);
          setter(result);
          nameSetter(file.name);
        } catch {
          errorSetter('Invalid JSON file. Please select a valid results.json file.');
        }
      };
      reader.onerror = () => errorSetter('Failed to read file.');
      reader.readAsText(file);
    },
    []
  );

  const handleDrop = useCallback(
    (e, fileIndex) => {
      e.preventDefault();
      if (fileIndex === 1) setDragOver1(false);
      else setDragOver2(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        if (fileIndex === 1) parseAndLoad(file, setData1, setFileName1, setError1);
        else parseAndLoad(file, setData2, setFileName2, setError2);
      }
    },
    [parseAndLoad]
  );

  const handleFileSelect = useCallback(
    (e, fileIndex) => {
      const file = e.target.files[0];
      if (file) {
        if (fileIndex === 1) parseAndLoad(file, setData1, setFileName1, setError1);
        else parseAndLoad(file, setData2, setFileName2, setError2);
      }
    },
    [parseAndLoad]
  );

  const renderDropZone = (fileIndex, fileName, dragOver, setDragOver, error) => (
    <div
      className={'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ' +
        (dragOver
          ? 'border-cyan-400 bg-cyan-50'
          : 'border-gray-300 hover:border-gray-400 bg-white')}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => handleDrop(e, fileIndex)}
      onClick={() => document.getElementById('file-input-' + fileIndex)?.click()}
    >
      <input
        id={'file-input-' + fileIndex}
        type="file"
        accept=".json"
        className="hidden"
        onChange={(e) => handleFileSelect(e, fileIndex)}
      />
      {fileName ? (
        <div>
          <p className="text-cyan-600 text-lg font-semibold">✓ {fileName}</p>
          <p className="text-gray-400 text-sm mt-1">Click to load a different file</p>
        </div>
      ) : (
        <div>
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-gray-500 text-lg">
            Drag & drop <span className="text-cyan-600 font-semibold">results.json</span> here for Benchmark {fileIndex}
          </p>
          <p className="text-gray-400 text-sm mt-1">or click to browse</p>
        </div>
      )}
      {error && (
        <p className="text-red-500 text-sm mt-2 text-center">{error}</p>
      )}
    </div>
  );

  return (
    <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
      {renderDropZone(1, fileName1, dragOver1, setDragOver1, error1)}
      {renderDropZone(2, fileName2, dragOver2, setDragOver2, error2)}
    </div>
  );
}