function deleteRecord(recordId, recordType) {
            if (confirm(`Are you sure you want to delete this ${recordType}? This action cannot be undone.`)) {
                const form = new FormData();
                form.append('id', recordId);
                form.append('type', recordType);
                form.append('csrfmiddlewaretoken', '{{ csrf_token }}');

                fetch('{% url "superadmin:delete_record" %}', {
                    method: 'POST',
                    body: form
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }
