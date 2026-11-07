from django.shortcuts import render


def delete_account_page(request):
    return render(request, "accounts/delete_account.html")
