import { useState, useCallback, useEffect } from 'react';

export default function FileLoader({ onDataLoaded }) {
  const [benchmarks, setBenchmarks] = useState([]);
  const [errors, setErrors] = useState({});
  const [fileNames, setFileNames] = useState({});

  // Notify parent whenever benchmarks change
  useEffect(() => {
    const data = benchmarks.map(b => b.data);
    onDataLoaded(data);
  }, [benchmarks, onDataLoaded]);

  const parseAndLoadFiles = useCallback((files) => {
    const newBenchmarks = [];
    const newErrors = {};
    const newFileNames = {};

    Array.from(files).forEach((file, idx) => {
      if (!file.name.endsWith('.json')) return;

      const reader = new FileReader();
      const id = idx + 1;

      reader.onload = (e) => {
        try {
          const result = JSON.parse(e.target.result);
          newBenchmarks.push({ id, data: result });
          newFileNames[id] = file.name;
          newErrors[id] = null;
          
          // Update state after all files are processed
          if (Object.keys(newFileNames).length === files.length) {
            setBenchmarks(newBenchmarks);
            setFileNames(newFileNames);
            setErrors(newErrors);
          }
        } catch {
          newErrors[id] = 'Invalid JSON file.';
          newFileNames[id] = file.name;
          
          if (Object.keys(newFileNames).length === files.length) {
            setBenchmarks(newBenchmarks);
            setFileNames(newFileNames);
            setErrors(newErrors);
          }
        }
      };

      reader.onerror = () => {
        newErrors[id] = 'Failed to read file.';
        newFileNames[id] = file.name;
        
        if (Object.keys(newFileNames).length === files.length) {
          setBenchmarks(newBenchmarks);
          setFileNames(newFileNames);
          setErrors(newErrors);
        }
      };

      reader.readAsText(file);
    });

    // Handle empty file list
    if (files.length === 0) {
      setBenchmarks([]);
      setFileNames({});
      setErrors({});
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    parseAndLoadFiles(files);
  }, [parseAndLoadFiles]);

  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files);
    parseAndLoadFiles(files);
  }, [parseAndLoadFiles]);

  const removeBenchmark = useCallback((id) => {
    setBenchmarks(prev => {
      const filtered = prev.filter(b => b.id !== id);
      // Reassign IDs to maintain sequential numbering
      return filtered.map((b, idx) => ({ ...b, id: idx + 1 }));
    });
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[id];
      // Reassign error keys
      const reordered = {};
      Object.keys(newErrors).sort((a, b) => parseInt(a) - parseInt(b)).forEach((key, idx) => {
        reordered[idx + 1] = newErrors[key];
      });
      return reordered;
    });
    setFileNames(prev => {
      const newNames = { ...prev };
      delete newNames[id];
      // Reassign name keys
      const reordered = {};
      Object.keys(newNames).sort((a, b) => parseInt(a) - parseInt(b)).forEach((key, idx) => {
        reordered[idx + 1] = newNames[key];
      });
      return reordered;
    });
  }, []);

  const renderDropZone = (benchmark) => {
    const { id, data } = benchmark;
    const fileName = fileNames[id];
    const error = errors[id];
    const hasData = !!data;

    return (
      <div
        key={id}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors relative ${
          hasData
            ? 'border-cyan-400 bg-cyan-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          e.currentTarget.classList.add('border-cyan-400');
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          if (!hasData) e.currentTarget.classList.remove('border-cyan-400');
        }}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".json"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            removeBenchmark(id);
          }}
          className="absolute top-2 right-2 text-gray-400 hover:text-red-500 transition-colors rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-50"
          title="Remove this file"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        {fileName ? (
          <div>
            <p className="text-cyan-600 text-lg font-semibold">✓ {fileName}</p>
            <p className="text-gray-400 text-sm mt-1">Click to replace with different file(s)</p>
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
            <p className="text-gray-500 text-sm">
              Drop benchmark JSON files here or click to browse
            </p>
            <p className="text-gray-400 text-xs mt-1">(Select multiple files with Ctrl/Cmd + Click)</p>
          </div>
        )}
        {error && (
          <p className="text-red-500 text-sm mt-2 text-center">{error}</p>
        )}
      </div>
    );
  };

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        {benchmarks.map((benchmark) => renderDropZone(benchmark))}
      </div>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          e.currentTarget.classList.add('border-cyan-400');
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          e.currentTarget.classList.remove('border-cyan-400');
        }}
        onClick={() => document.getElementById('file-input-add')?.click()}
        className="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center cursor-pointer hover:border-cyan-400 hover:bg-cyan-50 transition-colors"
      >
        <input
          id="file-input-add"
          type="file"
          accept=".json"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
        <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <p className="text-gray-500 text-sm">
          + Add More Files
        </p>
        <p className="text-gray-400 text-xs mt-1">Drag & drop or click to browse</p>
      </div>
    </div>
  );
}