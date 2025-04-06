$(document).ready(function() {
    // Initialize DataTable
    const table = $('#volunteerTable').DataTable({
        ajax: {
            url: '/admin/get_all_volunteers',
            dataSrc: ''
        },
        columns: [
            { data: 'id' },
            { data: 'name' },
            { data: 'email' },
            { data: 'phone' },
            { data: 'location' },
            { data: 'status' },
            {
                data: null,
                render: function(data, type, row) {
                    const statusButtons = `
                        <button class="btn btn-sm btn-success approve-btn" ${row.status === 'approved' ? 'disabled' : ''}>
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-danger reject-btn" ${row.status === 'rejected' ? 'disabled' : ''}>
                            <i class="fas fa-times"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-btn">
                            <i class="fas fa-trash"></i>
                        </button>
                    `;
                    return statusButtons;
                }
            }
        ]
    });

    // Handle form submission
    $('#saveVolunteer').click(function() {
        const formData = {
            name: $('#name').val(),
            email: $('#email').val(),
            phone: $('#phone').val(),
            location: $('#location').val()
        };

        $.ajax({
            url: '/admin/add_volunteer',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#addVolunteerModal').modal('hide');
                table.ajax.reload();
                toastr.success('Volunteer added successfully');
                $('#addVolunteerForm')[0].reset();
            },
            error: function(xhr) {
                toastr.error(xhr.responseJSON.error || 'Error adding volunteer');
            }
        });
    });

    // Handle approve button click
    $('#volunteerTable').on('click', '.approve-btn', function() {
        const data = table.row($(this).closest('tr')).data();
        updateVolunteerStatus(data.id, 'approved', table);
    });

    // Handle reject button click
    $('#volunteerTable').on('click', '.reject-btn', function() {
        const data = table.row($(this).closest('tr')).data();
        updateVolunteerStatus(data.id, 'rejected', table);
    });

    // Handle delete button click
    $('#volunteerTable').on('click', '.delete-btn', function() {
        const data = table.row($(this).closest('tr')).data();
        if (confirm('Are you sure you want to delete this volunteer?')) {
            $.ajax({
                url: `/admin/delete_volunteer/${data.id}`,
                type: 'DELETE',
                success: function() {
                    table.ajax.reload();
                    toastr.success('Volunteer deleted successfully');
                },
                error: function(xhr) {
                    toastr.error(xhr.responseJSON.error || 'Error deleting volunteer');
                }
            });
        }
    });
});

function updateVolunteerStatus(volunteerId, status, table) {
    $.ajax({
        url: `/admin/update_volunteer/${volunteerId}`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ status: status }),
        success: function() {
            table.ajax.reload();
            toastr.success(`Volunteer ${status} successfully`);
        },
        error: function(xhr) {
            toastr.error(xhr.responseJSON.error || `Error ${status} volunteer`);
        }
    });
} 