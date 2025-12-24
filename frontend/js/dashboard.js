function dashboardApp() {
    return {
        // State
        currentTab: 'upload',
        userEmail: '',
        userInitial: '',
        token: '',
        
        // Data
        documents: [],
        summaries: [],
        stats: {
            total_documents: 0,
            total_words: 0,
            total_size_mb: 0,
            file_types: {}
        },
        
        // UI State
        loading: false,
        uploading: false,
        generatingSummary: false,
        isDragging: false,
        selectedFile: null,
        summaryResult: null,
        
        alert: {
            show: false,
            type: 'info',
            message: ''
        },

        // Initialize
        init() {
            // Check authentication
            this.token = localStorage.getItem('token');
            this.userEmail = localStorage.getItem('userEmail') || 'User';
            
            if (!this.token) {
                window.location.href = 'login.html';
                return;
            }

            // Set user initial
            this.userInitial = this.userEmail.charAt(0).toUpperCase();
            
            // Load initial data
            this.loadStats();
            this.loadDocuments();
        },

        // API Helper
        async apiCall(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    ...options.headers
                }
            };

            const response = await fetch(url, { ...options, ...defaultOptions });
            
            if (response.status === 401) {
                this.logout();
                return null;
            }

            return response;
        },

        // Load Stats
        async loadStats() {
            try {
                const response = await this.apiCall('http://localhost:8000/documents/stats');
                if (response && response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        },

        // Load Documents
        async loadDocuments() {
            this.loading = true;
            try {
                const response = await this.apiCall('http://localhost:8000/documents/');
                if (response && response.ok) {
                    const data = await response.json();
                    this.documents = data.documents;
                }
            } catch (error) {
                console.error('Failed to load documents:', error);
                this.showAlert('error', 'Failed to load documents');
            } finally {
                this.loading = false;
            }
        },

        // Load Summaries
        async loadSummaries() {
            this.loading = true;
            try {
                const response = await this.apiCall('http://localhost:8000/summaries/');
                if (response && response.ok) {
                    const data = await response.json();
                    this.summaries = data.summaries;
                }
            } catch (error) {
                console.error('Failed to load summaries:', error);
                this.showAlert('error', 'Failed to load summaries');
            } finally {
                this.loading = false;
            }
        },

        // File Upload Handlers
        handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                this.selectedFile = file;
            }
        },

        handleDrop(event) {
            this.isDragging = false;
            const file = event.dataTransfer.files[0];
            if (file) {
                this.selectedFile = file;
            }
        },

        // Upload Document
        async uploadDocument() {
            if (!this.selectedFile) return;

            this.uploading = true;
            
            try {
                const formData = new FormData();
                formData.append('file', this.selectedFile);

                const response = await this.apiCall('http://localhost:8000/documents/upload', {
                    method: 'POST',
                    body: formData,
                    headers: {} // Let browser set Content-Type for FormData
                });

                if (response && response.ok) {
                    this.showAlert('success', 'Document uploaded successfully!');
                    this.selectedFile = null;
                    this.$refs.fileInput.value = '';
                    
                    // Reload data
                    await this.loadDocuments();
                    await this.loadStats();
                    
                    // Switch to documents tab
                    this.currentTab = 'documents';
                } else {
                    const error = await response.json();
                    this.showAlert('error', error.detail || 'Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                this.showAlert('error', 'Upload failed. Please try again.');
            } finally {
                this.uploading = false;
            }
        },

        // Generate Summary
        async generateSummary(documentId) {
            this.generatingSummary = true;
            this.summaryResult = null;
            this.$refs.summaryModal.showModal();

            try {
                const response = await this.apiCall('http://localhost:8000/summaries/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        document_id: documentId,
                        max_length: 150,
                        min_length: 50
                    })
                });

                if (response && response.ok) {
                    this.summaryResult = await response.json();
                    this.showAlert('success', 'Summary generated successfully!');
                } else {
                    const error = await response.json();
                    this.showAlert('error', error.detail || 'Failed to generate summary');
                    this.closeSummaryModal();
                }
            } catch (error) {
                console.error('Summary generation error:', error);
                this.showAlert('error', 'Failed to generate summary');
                this.closeSummaryModal();
            } finally {
                this.generatingSummary = false;
            }
        },

        closeSummaryModal() {
            this.$refs.summaryModal.close();
            this.summaryResult = null;
        },

        // Delete Document
        async deleteDocument(documentId) {
            if (!confirm('Are you sure you want to delete this document?')) return;

            try {
                const response = await this.apiCall(`http://localhost:8000/documents/${documentId}`, {
                    method: 'DELETE'
                });

                if (response && response.ok) {
                    this.showAlert('success', 'Document deleted');
                    await this.loadDocuments();
                    await this.loadStats();
                } else {
                    this.showAlert('error', 'Failed to delete document');
                }
            } catch (error) {
                console.error('Delete error:', error);
                this.showAlert('error', 'Failed to delete document');
            }
        },

        // Delete Summary
        async deleteSummary(summaryId) {
            if (!confirm('Are you sure you want to delete this summary?')) return;

            try {
                const response = await this.apiCall(`http://localhost:8000/summaries/${summaryId}`, {
                    method: 'DELETE'
                });

                if (response && response.ok) {
                    this.showAlert('success', 'Summary deleted');
                    await this.loadSummaries();
                } else {
                    this.showAlert('error', 'Failed to delete summary');
                }
            } catch (error) {
                console.error('Delete error:', error);
                this.showAlert('error', 'Failed to delete summary');
            }
        },

        // Logout
        logout() {
            localStorage.removeItem('token');
            localStorage.removeItem('userEmail');
            window.location.href = 'login.html';
        },

        // Helpers
        showAlert(type, message) {
            this.alert = { show: true, type, message };
            setTimeout(() => {
                this.alert.show = false;
            }, 5000);
        },

        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        formatFileSize(bytes) {
            if (!bytes) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
    }
}