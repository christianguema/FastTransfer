#fonction d'insertion d'un compte admin de l'application
from django.contrib.auth.models import Group
from userauths.models import User

def create_admin_account():
    # Vérifier si le groupe "admins" existe, sinon le créer
    admin_group, created = Group.objects.get_or_create(name='admins')

    # Vérifier si un utilisateur admin existe déjà
   
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpassword',
        first_name='Admin',
        # gender="F",
        # phone="92-89-85-66",
        last_name='User',
        is_staff=True,
        is_superuser=True
    )

    # Ajouter l'utilisateur au groupe "admins"
    admin_user.groups.add(admin_group)
    admin_user.save()

    print("Compte administrateur créé avec succès.")
   

# Appeler la fonction pour créer le compte admin
create_admin_account()


#fonction pour supprimer le seeder de l'admin
def delete_admin_account():
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.delete()
        print("Compte administrateur supprimé avec succès.")
    except User.DoesNotExist:
        print("Aucun compte administrateur trouvé à supprimer.")