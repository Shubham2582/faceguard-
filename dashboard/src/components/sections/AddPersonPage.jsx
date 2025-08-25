import React, { useState, useRef } from 'react';
import {
  Upload, User, Users, Camera, FileText, Folder, Plus, X, Loader2, CheckCircle,
  Save, RotateCcw, Image as ImageIcon, Mail, Phone, Shield, Building, CreditCard,
  AlertTriangle, Info
} from 'lucide-react';
import { MinimalCard, MinimalCardContent, MinimalCardTitle } from '@/components/ui/MinimalCard';
import { personAPI } from '@/services/api';

export const AddPersonPage = ({ onNavigate }) => {
  const [enrollmentMode, setEnrollmentMode] = useState('individual');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [enrollmentComplete, setEnrollmentComplete] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const [enrollmentResult, setEnrollmentResult] = useState(null);
  
  const [formData, setFormData] = useState({
    firstName: '', lastName: '', email: '', phone: '', employeeId: '',
    department: '', position: '', riskLevel: 'low', accessLevel: 'standard',
    enrollmentImages: []
  });

  const [batchData, setBatchData] = useState(null);
  const [folderStructure, setFolderStructure] = useState([]);
  const imageInputRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = (files) => {
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
    const newImages = imageFiles.map(file => ({
      file, url: URL.createObjectURL(file), id: Math.random().toString(36).substr(2, 9)
    }));
    setFormData(prev => ({ ...prev, enrollmentImages: [...prev.enrollmentImages, ...newImages] }));
  };

  const removeImage = (imageId) => {
    setFormData(prev => ({
      ...prev, enrollmentImages: prev.enrollmentImages.filter(img => img.id !== imageId)
    }));
  };

  const handleBatchUpload = (files) => {
    const jsonFile = Array.from(files).find(file => file.name.endsWith('.json'));
    if (jsonFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try { setBatchData(JSON.parse(e.target.result)); } catch (error) { 
          setError('Invalid JSON file format'); 
          console.error('Invalid JSON'); 
        }
      };
      reader.readAsText(jsonFile);
    }
  };

  const handleFolderUpload = (files) => {
    const fileArray = Array.from(files);
    const structure = {};
    
    fileArray.forEach(file => {
      const pathParts = file.webkitRelativePath.split('/');
      if (pathParts.length >= 2) {
        const personName = pathParts[pathParts.length - 2]; // Get the folder name
        
        if (!structure[personName]) {
          structure[personName] = [];
        }
        
        if (file.type.startsWith('image/')) {
          structure[personName].push({
            file,
            url: URL.createObjectURL(file),
            name: file.name
          });
        }
      }
    });
    
    // Filter out persons with no images
    const validStructure = Object.entries(structure)
      .filter(([name, images]) => images.length > 0)
      .map(([name, images]) => ({
        name,
        images,
        id: Math.random().toString(36).substr(2, 9)
      }));
    
    setFolderStructure(validStructure);
  };

  const performEnrollment = async () => {
    setIsProcessing(true);
    setProcessingProgress(0);
    setError(null);
    
    try {
      // Validate required fields
      if (!formData.firstName || !formData.lastName || !formData.email || !formData.employeeId) {
        throw new Error('Please fill in all required fields');
      }
      
      if (formData.enrollmentImages.length < 1) {
        throw new Error('Please upload at least one training image');
      }

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProcessingProgress(prev => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 15 + 5;
        });
      }, 300);

      let result;
      
      if (enrollmentMode === 'individual') {
        // Individual enrollment with images
        result = await personAPI.createWithImages(formData, formData.enrollmentImages);
      } else if (enrollmentMode === 'batch' && batchData) {
        // Batch enrollment
        const metadataFile = new File([JSON.stringify(batchData)], 'batch_metadata.json', {
          type: 'application/json'
        });
        // Note: For demo, we don't have actual images zip file
        // In real implementation, user would upload both metadata and images zip
        result = await personAPI.batchEnroll(metadataFile, null, true);
      } else if (enrollmentMode === 'folder' && folderStructure.length > 0) {
        // Folder structure enrollment
        // Process each person in the folder structure
        const results = [];
        for (const person of folderStructure) {
          const personData = {
            firstName: person.name.split(' ')[0] || person.name,
            lastName: person.name.split(' ').slice(1).join(' ') || '',
            email: `${person.name.toLowerCase().replace(/\s+/g, '.')}@company.com`,
            employeeId: `EMP-${Math.random().toString(36).substr(2, 6).toUpperCase()}`,
            department: formData.department || 'General',
            position: formData.position || 'Employee',
            accessLevel: formData.accessLevel,
            riskLevel: formData.riskLevel
          };
          
          const personResult = await personAPI.createWithImages(personData, person.images);
          results.push(personResult);
        }
        result = { batch_results: results, total_processed: results.length };
      }

      clearInterval(progressInterval);
      setProcessingProgress(100);
      setEnrollmentResult(result);
      setEnrollmentComplete(true);
      
    } catch (error) {
      console.error('Enrollment failed:', error);
      setError(error.message || 'Enrollment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    
    if (enrollmentMode === 'batch') {
      handleBatchUpload(files);
    } else if (enrollmentMode === 'folder') {
      handleFolderUpload(files);
    } else {
      handleImageUpload(files);
    }
  };

  const resetForm = () => {
    setFormData({
      firstName: '', lastName: '', email: '', phone: '', employeeId: '',
      department: '', position: '', riskLevel: 'low', accessLevel: 'standard',
      enrollmentImages: []
    });
    setEnrollmentComplete(false); 
    setBatchData(null); 
    setFolderStructure([]);
    setError(null);
    setEnrollmentResult(null);
  };

  if (enrollmentComplete) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-24 h-24 bg-emerald-600/20 rounded-full flex items-center justify-center mx-auto mb-8">
            <CheckCircle className="h-12 w-12 text-emerald-400" />
          </div>
          <h2 className="text-3xl font-normal text-white mb-4">Enrollment Completed Successfully</h2>
          <p className="text-zinc-400 text-lg mb-8 max-w-md mx-auto">
            {enrollmentMode === 'individual' 
              ? `${formData.firstName} ${formData.lastName} has been enrolled in the system.`
              : enrollmentMode === 'batch'
              ? `${batchData?.persons?.length || 0} persons have been enrolled successfully.`
              : `${folderStructure.length} persons have been enrolled from folder structure.`
            }
          </p>
          
          {/* Show enrollment details */}
          {enrollmentResult && (
            <div className="bg-zinc-950/30 border border-zinc-800 rounded-lg p-4 mb-8 max-w-lg mx-auto">
              <h3 className="text-sm font-medium text-emerald-400 mb-2">Enrollment Details</h3>
              {enrollmentMode === 'individual' && (
                <div className="text-sm text-zinc-300">
                  <p>Person ID: <span className="text-white">{enrollmentResult.person_id || formData.employeeId}</span></p>
                  <p>Status: <span className="text-emerald-400">Active</span></p>
                  {enrollmentResult.face_count && (
                    <p>Images Processed: <span className="text-white">{enrollmentResult.face_count}</span></p>
                  )}
                </div>
              )}
              {enrollmentMode !== 'individual' && enrollmentResult.total_processed && (
                <div className="text-sm text-zinc-300">
                  <p>Total Processed: <span className="text-white">{enrollmentResult.total_processed}</span></p>
                  <p>Batch Status: <span className="text-emerald-400">Completed</span></p>
                </div>
              )}
            </div>
          )}
          <div className="flex gap-4 justify-center">
            <button onClick={resetForm} className="flex items-center gap-2 px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors">
              <Plus className="h-4 w-4" />Enroll Another
            </button>
            <button onClick={() => onNavigate('persons')} className="flex items-center gap-2 px-6 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-600/30 transition-colors">
              <Users className="h-4 w-4" />View Enrolled Persons
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Error Alert */}
      {error && (
        <div className="mb-8">
          <MinimalCard className="border-red-900/50 bg-red-950/20">
            <MinimalCardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-600/20 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                </div>
                <div>
                  <h3 className="text-red-400 font-medium mb-1">Enrollment Error</h3>
                  <p className="text-zinc-300 text-sm">{error}</p>
                </div>
                <button 
                  onClick={() => setError(null)}
                  className="ml-auto p-1 hover:bg-red-600/20 rounded transition-colors"
                >
                  <X className="h-4 w-4 text-red-400" />
                </button>
              </div>
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}

      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-block bg-emerald-600/10 border border-emerald-600/20 text-emerald-400 px-4 py-2 rounded-full text-xs font-medium mb-10 tracking-wider">
          ENROLLMENT
        </div>
        <h1 className="text-5xl lg:text-6xl font-normal mb-8 tracking-tight leading-tight">
          Add New <span className="italic text-zinc-600 font-light">Person</span>
        </h1>
        <p className="text-zinc-500 text-lg max-w-4xl mx-auto leading-relaxed">
          Enroll individuals into the facial recognition system with comprehensive profile management and batch processing capabilities.
        </p>
      </div>

      {/* Enrollment Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        {[
          { mode: 'individual', icon: User, color: 'emerald', title: 'Individual Enrollment', desc: 'Add a single person with detailed profile information and multiple images for optimal recognition accuracy.', badge: 'Recommended for new employees' },
          { mode: 'batch', icon: FileText, color: 'blue', title: 'Batch Upload (JSON)', desc: 'Upload multiple persons using a structured JSON file with pre-defined format for bulk enrollment operations.', badge: 'Ideal for large datasets' },
          { mode: 'folder', icon: Folder, color: 'purple', title: 'Folder Structure', desc: 'Upload organized folders where each person has their own directory containing multiple training images.', badge: 'Perfect for organized datasets' }
        ].map(({ mode, icon: Icon, color, title, desc, badge }) => (
          <MinimalCard key={mode} className={`cursor-pointer transition-all duration-300 ${enrollmentMode === mode ? `ring-2 ring-${color}-500/50 bg-${color}-950/20 border-${color}-600/50` : 'hover:scale-[1.02]'}`} onClick={() => setEnrollmentMode(mode)}>
            <MinimalCardContent className="p-8 text-center">
              <div className={`p-4 bg-${color}-600/20 rounded-lg mb-6 w-fit mx-auto`}>
                <Icon className={`h-8 w-8 text-${color}-400`} />
              </div>
              <MinimalCardTitle className="text-xl mb-4">{title}</MinimalCardTitle>
              <p className="text-zinc-400 text-sm mb-6 leading-relaxed">{desc}</p>
              <div className={`text-xs text-${color}-400 bg-${color}-950/50 px-3 py-1.5 rounded-full border border-${color}-600/30`}>{badge}</div>
            </MinimalCardContent>
          </MinimalCard>
        ))}
      </div>

      {/* Individual Enrollment Form */}
      {enrollmentMode === 'individual' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          <div className="lg:col-span-2">
            <MinimalCard>
              <MinimalCardContent className="p-8">
                <div className="flex items-center gap-3 mb-8">
                  <div className="p-2 bg-emerald-600/20 rounded-lg">
                    <User className="h-5 w-5 text-emerald-400" />
                  </div>
                  <h2 className="text-2xl font-normal text-white">Personal Information</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  {[
                    { field: 'firstName', label: 'First Name *', placeholder: 'Enter first name', required: true },
                    { field: 'lastName', label: 'Last Name *', placeholder: 'Enter last name', required: true },
                    { field: 'email', label: 'Email Address *', placeholder: 'person@company.com', type: 'email', icon: Mail, required: true },
                    { field: 'phone', label: 'Phone Number', placeholder: '+1 (555) 123-4567', type: 'tel', icon: Phone },
                    { field: 'employeeId', label: 'Employee ID *', placeholder: 'EMP-001', icon: CreditCard, required: true },
                    { field: 'position', label: 'Position', placeholder: 'Job title' }
                  ].map(({ field, label, placeholder, type = 'text', icon: Icon, required }) => (
                    <div key={field}>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">
                        {Icon && <Icon className="inline h-4 w-4 mr-1" />}{label}
                      </label>
                      <input
                        type={type}
                        value={formData[field]}
                        onChange={(e) => handleInputChange(field, e.target.value)}
                        className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 transition-colors"
                        placeholder={placeholder}
                        required={required}
                      />
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      <Building className="inline h-4 w-4 mr-1" />Department
                    </label>
                    <select value={formData.department} onChange={(e) => handleInputChange('department', e.target.value)} className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors">
                      <option value="">Select Department</option>
                      {['Engineering', 'Security', 'Administration', 'Operations', 'Human Resources', 'Finance', 'Marketing'].map(dept => (
                        <option key={dept} value={dept}>{dept}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      <Shield className="inline h-4 w-4 mr-1" />Risk Level
                    </label>
                    <select value={formData.riskLevel} onChange={(e) => handleInputChange('riskLevel', e.target.value)} className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors">
                      {['low', 'medium', 'high', 'critical'].map(level => (
                        <option key={level} value={level}>{level.charAt(0).toUpperCase() + level.slice(1)} Risk</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Access Level</label>
                    <select value={formData.accessLevel} onChange={(e) => handleInputChange('accessLevel', e.target.value)} className="w-full px-4 py-3 bg-zinc-950/50 border border-zinc-900 rounded-lg text-white focus:outline-none focus:border-emerald-500 transition-colors">
                      {['standard', 'elevated', 'restricted', 'administrative'].map(level => (
                        <option key={level} value={level}>{level.charAt(0).toUpperCase() + level.slice(1)} Access</option>
                      ))}
                    </select>
                  </div>
                </div>
              </MinimalCardContent>
            </MinimalCard>
          </div>

          <div>
            <MinimalCard>
              <MinimalCardContent className="p-8">
                <div className="flex items-center gap-3 mb-8">
                  <div className="p-2 bg-blue-600/20 rounded-lg">
                    <Camera className="h-5 w-5 text-blue-400" />
                  </div>
                  <h2 className="text-xl font-normal text-white">Training Images</h2>
                </div>

                <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${dragOver ? 'border-blue-500 bg-blue-950/20' : 'border-zinc-700 hover:border-zinc-600'}`}
                     onDrop={handleDrop} onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={(e) => { e.preventDefault(); setDragOver(false); }}>
                  <div className="p-4 bg-blue-600/20 rounded-lg mb-4 w-fit mx-auto">
                    <ImageIcon className="h-8 w-8 text-blue-400" />
                  </div>
                  <p className="text-white font-medium mb-2">Upload Training Images</p>
                  <p className="text-zinc-400 text-sm mb-4">Drag & drop multiple images or click to browse</p>
                  <p className="text-zinc-500 text-xs mb-6">Minimum 3 images recommended for best accuracy</p>
                  <button onClick={() => imageInputRef.current?.click()} className="px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors text-sm">
                    Browse Files
                  </button>
                  <input ref={imageInputRef} type="file" multiple accept="image/*" onChange={(e) => handleImageUpload(e.target.files)} className="hidden" />
                </div>

                {formData.enrollmentImages.length > 0 && (
                  <div className="mt-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm text-zinc-400">{formData.enrollmentImages.length} image(s) uploaded</span>
                      <div className={`px-2 py-1 rounded text-xs ${formData.enrollmentImages.length >= 3 ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-600/30' : 'bg-yellow-950/50 text-yellow-400 border border-yellow-600/30'}`}>
                        {formData.enrollmentImages.length >= 3 ? 'Optimal' : 'Need more'}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {formData.enrollmentImages.map((image) => (
                        <div key={image.id} className="relative group">
                          <img src={image.url} alt="Training" className="w-full h-24 object-cover rounded-lg" />
                          <button onClick={() => removeImage(image.id)} className="absolute top-1 right-1 p-1 bg-red-600/80 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </MinimalCardContent>
            </MinimalCard>
          </div>
        </div>
      )}

      {/* Batch Upload Mode */}
      {enrollmentMode === 'batch' && (
        <div className="mb-16">
          <MinimalCard>
            <MinimalCardContent className="p-8">
              <div className="flex items-center gap-3 mb-8">
                <div className="p-2 bg-blue-600/20 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-400" />
                </div>
                <h2 className="text-2xl font-normal text-white">Batch Upload via JSON</h2>
              </div>
              <div className={`border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300 ${dragOver ? 'border-blue-500 bg-blue-950/20' : 'border-zinc-700 hover:border-zinc-600'}`}
                   onDrop={handleDrop} onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={(e) => { e.preventDefault(); setDragOver(false); }}>
                <div className="p-6 bg-blue-600/20 rounded-lg mb-6 w-fit mx-auto">
                  <Upload className="h-12 w-12 text-blue-400" />
                </div>
                <h3 className="text-xl font-medium text-white mb-4">Upload JSON Configuration File</h3>
                <p className="text-zinc-400 mb-6 max-w-2xl mx-auto">Upload a JSON file containing structured person information for bulk enrollment.</p>
                <button onClick={() => fileInputRef.current?.click()} className="px-6 py-3 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-600/30 transition-colors">
                  Select JSON File
                </button>
                <input ref={fileInputRef} type="file" accept=".json" onChange={(e) => handleBatchUpload(e.target.files)} className="hidden" />
              </div>
              {batchData && (
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-white mb-4">JSON Preview - {batchData.persons?.length || 0} persons found</h3>
                  <div className="bg-zinc-950/50 border border-zinc-800 rounded-lg p-4 max-h-64 overflow-y-auto">
                    <pre className="text-sm text-zinc-300">{JSON.stringify(batchData, null, 2)}</pre>
                  </div>
                </div>
              )}
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}

      {/* Folder Structure Mode */}
      {enrollmentMode === 'folder' && (
        <div className="mb-16">
          <MinimalCard>
            <MinimalCardContent className="p-8">
              <div className="flex items-center gap-3 mb-8">
                <div className="p-2 bg-purple-600/20 rounded-lg">
                  <Folder className="h-5 w-5 text-purple-400" />
                </div>
                <h2 className="text-2xl font-normal text-white">Folder Structure Upload</h2>
              </div>

              <div className={`border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300 ${dragOver ? 'border-purple-500 bg-purple-950/20' : 'border-zinc-700 hover:border-zinc-600'}`}
                   onDrop={handleDrop} onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={(e) => { e.preventDefault(); setDragOver(false); }}>
                <div className="p-6 bg-purple-600/20 rounded-lg mb-6 w-fit mx-auto">
                  <Upload className="h-12 w-12 text-purple-400" />
                </div>
                <h3 className="text-xl font-medium text-white mb-4">Upload Organized Folder Structure</h3>
                <p className="text-zinc-400 mb-6 max-w-2xl mx-auto">
                  Select organized folders where each person has their own directory with multiple training images.
                </p>
                <p className="text-zinc-500 text-sm mb-6">
                  Expected structure: MainFolder/PersonName/image1.jpg, MainFolder/PersonName/image2.jpg...
                </p>
                <button 
                  onClick={() => {
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.webkitdirectory = true;
                    input.multiple = true;
                    input.onchange = (e) => handleFolderUpload(e.target.files);
                    input.click();
                  }} 
                  className="px-6 py-3 bg-purple-600/20 hover:bg-purple-600/30 text-purple-400 rounded-lg border border-purple-600/30 transition-colors"
                >
                  Select Folder
                </button>
              </div>

              {folderStructure.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-white mb-4">
                    Folder Preview - {folderStructure.length} persons found
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {folderStructure.map((person) => (
                      <div key={person.id} className="bg-zinc-950/30 border border-zinc-800 rounded-lg p-4">
                        <h4 className="text-white font-medium mb-2">{person.name}</h4>
                        <p className="text-zinc-400 text-sm mb-3">{person.images.length} images</p>
                        <div className="grid grid-cols-3 gap-2">
                          {person.images.slice(0, 3).map((image, idx) => (
                            <img
                              key={idx}
                              src={image.url}
                              alt={`${person.name} ${idx + 1}`}
                              className="w-full h-16 object-cover rounded"
                            />
                          ))}
                          {person.images.length > 3 && (
                            <div className="w-full h-16 bg-zinc-800 rounded flex items-center justify-center">
                              <span className="text-xs text-zinc-400">+{person.images.length - 3}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between mb-8">
        <button onClick={resetForm} className="flex items-center gap-2 px-6 py-3 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-400 rounded-lg border border-zinc-700 transition-colors">
          <RotateCcw className="h-4 w-4" />Reset Form
        </button>
        
        <div className="flex items-center gap-4">
          {/* Validation Info */}
          {enrollmentMode === 'individual' && (
            <div className="text-sm text-zinc-500">
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4" />
                {!formData.firstName || !formData.lastName || !formData.email || !formData.employeeId ? (
                  <span className="text-yellow-400">Required fields missing</span>
                ) : formData.enrollmentImages.length < 1 ? (
                  <span className="text-yellow-400">Upload at least 1 image</span>
                ) : formData.enrollmentImages.length < 3 ? (
                  <span className="text-yellow-400">3+ images recommended</span>
                ) : (
                  <span className="text-emerald-400">Ready for enrollment</span>
                )}
              </div>
            </div>
          )}
          
          {enrollmentMode === 'batch' && batchData && (
            <div className="text-sm text-emerald-400">
              {batchData.persons?.length || 0} persons ready
            </div>
          )}
          
          {enrollmentMode === 'folder' && folderStructure.length > 0 && (
            <div className="text-sm text-emerald-400">
              {folderStructure.length} persons ready
            </div>
          )}
          
          <button 
            onClick={performEnrollment} 
            disabled={isProcessing || (
              enrollmentMode === 'individual' && (!formData.firstName || !formData.lastName || !formData.email || !formData.employeeId || formData.enrollmentImages.length < 1)
            ) || (
              enrollmentMode === 'batch' && !batchData
            ) || (
              enrollmentMode === 'folder' && folderStructure.length === 0
            )} 
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-600/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing... {Math.round(processingProgress)}%
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                {enrollmentMode === 'individual' ? 'Enroll Person' : 
                 enrollmentMode === 'batch' ? 'Process Batch' : 'Process Folder'}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Processing Modal */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <MinimalCard className="w-full max-w-md">
            <MinimalCardContent className="p-8 text-center">
              <div className="p-4 bg-emerald-600/20 rounded-lg mb-6 w-fit mx-auto">
                <Loader2 className="h-8 w-8 text-emerald-400 animate-spin" />
              </div>
              <h3 className="text-xl font-medium text-white mb-4">Processing Enrollment</h3>
              <p className="text-zinc-400 mb-6">Analyzing facial features and generating embeddings...</p>
              <div className="w-full bg-zinc-800 rounded-full h-2 mb-4">
                <div className="bg-emerald-500 h-2 rounded-full transition-all duration-300" style={{ width: `${processingProgress}%` }}></div>
              </div>
              <p className="text-zinc-500 text-sm">{Math.round(processingProgress)}% Complete</p>
            </MinimalCardContent>
          </MinimalCard>
        </div>
      )}
    </>
  );
};