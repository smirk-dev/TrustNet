import { useState, useCallback } from "react";
import { Upload, FileText, Image, X, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";

interface FileUploadProps {
  onTextExtracted: (text: string, filename: string) => void;
  disabled?: boolean;
}

interface UploadedFile {
  file: File;
  id: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  extractedText?: string;
  error?: string;
}

export const FileUpload = ({ onTextExtracted, disabled }: FileUploadProps) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const { toast } = useToast();

  const extractTextFromImage = async (file: File): Promise<string> => {
    // Simulated OCR functionality - in a real app, you'd use Tesseract.js or similar
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`[OCR Text from ${file.name}] This is sample extracted text from the image. In a real implementation, this would use OCR technology to extract actual text from the uploaded image.`);
      }, 2000);
    });
  };

  const extractTextFromPDF = async (file: File): Promise<string> => {
    // Simulated PDF text extraction - in a real app, you'd use PDF.js or similar
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`[PDF Text from ${file.name}] This is sample extracted text from the PDF document. In a real implementation, this would parse the actual PDF content and extract all readable text.`);
      }, 1500);
    });
  };

  const processFile = async (uploadedFile: UploadedFile) => {
    const { file } = uploadedFile;
    
    try {
      setUploadedFiles(prev => 
        prev.map(f => f.id === uploadedFile.id ? { ...f, status: 'processing', progress: 50 } : f)
      );

      let extractedText = '';
      
      if (file.type.startsWith('image/')) {
        extractedText = await extractTextFromImage(file);
      } else if (file.type === 'application/pdf') {
        extractedText = await extractTextFromPDF(file);
      } else {
        throw new Error('Unsupported file type');
      }

      setUploadedFiles(prev => 
        prev.map(f => f.id === uploadedFile.id ? { 
          ...f, 
          status: 'completed', 
          progress: 100, 
          extractedText 
        } : f)
      );

      onTextExtracted(extractedText, file.name);
      
      toast({
        title: "Text Extracted Successfully",
        description: `Text has been extracted from ${file.name} and is ready for analysis.`,
        duration: 3000,
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process file';
      
      setUploadedFiles(prev => 
        prev.map(f => f.id === uploadedFile.id ? { 
          ...f, 
          status: 'error', 
          error: errorMessage 
        } : f)
      );

      toast({
        title: "Processing Failed",
        description: errorMessage,
        variant: "destructive",
        duration: 5000,
      });
    }
  };

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files || disabled) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    Array.from(files).forEach(file => {
      if (!validTypes.includes(file.type)) {
        toast({
          title: "Invalid File Type",
          description: "Please upload images (JPEG, PNG, WebP) or PDF files only.",
          variant: "destructive",
          duration: 5000,
        });
        return;
      }

      if (file.size > maxSize) {
        toast({
          title: "File Too Large",
          description: "Please upload files smaller than 10MB.",
          variant: "destructive",
          duration: 5000,
        });
        return;
      }

      const uploadedFile: UploadedFile = {
        file,
        id: Math.random().toString(36).substring(7),
        status: 'uploading',
        progress: 0,
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);
      
      // Simulate upload progress
      setTimeout(() => {
        setUploadedFiles(prev => 
          prev.map(f => f.id === uploadedFile.id ? { ...f, progress: 100 } : f)
        );
        processFile(uploadedFile);
      }, 500);
    });
  }, [disabled, onTextExtracted, toast]);

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card className="relative overflow-hidden">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={`
            border-2 border-dashed border-border/50 rounded-lg p-8 text-center transition-all duration-300
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary/50 hover:bg-gradient-card/50 cursor-pointer'}
          `}
        >
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 rounded-full bg-gradient-card border border-border/20">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Upload Images or PDFs</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Drag and drop files here, or click to browse. We'll extract text from your files for analysis.
              </p>
              <p className="text-xs text-muted-foreground">
                Supports: JPEG, PNG, WebP, PDF • Max size: 10MB
              </p>
            </div>

            <Button
              variant="outline"
              disabled={disabled}
              className="bg-gradient-card hover:bg-gradient-trust hover:text-white transition-all duration-300"
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.multiple = true;
                input.accept = 'image/jpeg,image/png,image/webp,application/pdf';
                input.onchange = (e) => {
                  const target = e.target as HTMLInputElement;
                  handleFileSelect(target.files);
                };
                input.click();
              }}
            >
              Select Files
            </Button>
          </div>
        </div>
      </Card>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-muted-foreground">Uploaded Files</h4>
          {uploadedFiles.map((uploadedFile) => (
            <Card key={uploadedFile.id} className="p-4 bg-gradient-card border border-border/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="p-2 rounded-lg bg-background/50">
                    {uploadedFile.file.type.startsWith('image/') ? (
                      <Image className="h-4 w-4 text-primary" />
                    ) : (
                      <FileText className="h-4 w-4 text-primary" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{uploadedFile.file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(uploadedFile.file.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    {uploadedFile.status === 'error' && (
                      <AlertCircle className="h-4 w-4 text-destructive" />
                    )}
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(uploadedFile.id)}
                      className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {uploadedFile.status !== 'completed' && uploadedFile.status !== 'error' && (
                <div className="mt-3 space-y-2">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>
                      {uploadedFile.status === 'uploading' ? 'Uploading...' : 'Processing...'}
                    </span>
                    <span>{uploadedFile.progress}%</span>
                  </div>
                  <Progress value={uploadedFile.progress} className="h-2" />
                </div>
              )}

              {uploadedFile.status === 'error' && (
                <div className="mt-2 p-2 rounded bg-destructive/10 border border-destructive/20">
                  <p className="text-xs text-destructive">{uploadedFile.error}</p>
                </div>
              )}

              {uploadedFile.status === 'completed' && uploadedFile.extractedText && (
                <div className="mt-3 p-3 rounded bg-background/50 border border-border/20">
                  <p className="text-xs text-muted-foreground mb-1">Extracted Text Preview:</p>
                  <p className="text-sm line-clamp-2">{uploadedFile.extractedText}</p>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};