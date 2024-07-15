from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from .models import UserProfile, Valoracion, Inventario, Fecha
from django.contrib.auth.decorators import login_required
from .forms import ValoracionForm, UserForm, InventarioForm, FechaForm
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def es_superusuario(user):
    return user.is_superuser

def acceso_denegado(request):
    return render(request, 'acceso_denegado.html')

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Importante para mantener la sesión del usuario
            messages.success(request, 'Tu contraseña ha sido actualizada con éxito!')
            return redirect('dashboard')  # O la página que prefieras
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'cambiar_password.html', {
        'form': form
    })

def registrarme(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        if 'password1' in request.POST:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 and password2:
                if password1 == password2:
                    try:
                        existing_user = UserProfile.objects.get(numero=request.POST['numero'])
                        error_message = 'El número de documento ya está en uso'
                    except UserProfile.DoesNotExist:
                        try:
                            user = UserProfile.objects.create(
                                tipo=request.POST['type'],
                                numero=request.POST['numero'],
                                username=request.POST['username'],
                                email=request.POST['email'],
                                password=password1
                            )
                            user.set_password(password1)
                            user.save()
                            success_message = 'Cuenta Creada Correctamente, Por favor inicie sesión'
                        except IntegrityError as e:
                            if 'unique constraint' in str(e):
                                error_message = 'El usuario ya fue creado'
                            else:
                                error_message = f'Error al crear el usuario: {e}'
                else:
                    error_message = 'Las contraseñas no coinciden'
        else:
            numero = request.POST.get('numer')
            password = request.POST.get('contra')
            user = authenticate(request, username=numero, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error_message = 'Credenciales inválidas'

    context = {
        'error': error_message,
        'done': success_message
    }
    return render(request, 'loginregister.html', context)

@login_required
def listhistorias(request):
    if request.user.is_superuser:
        historias = Valoracion.objects.all()
    else:
        historias = Valoracion.objects.filter(user=request.user)
    return render(request, 'historiaclinica/listhistorias.html', {'historias': historias})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def verhistorias(request, id):
    historia = Valoracion.objects.select_related('user').get(id=id)
    return render(request, 'historiaclinica/verhistorias.html', {'historia': historia})

@login_required
def fetch_user_details(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        numero = request.GET.get('numero')
        user = UserProfile.objects.filter(numero=numero).first()
        if user:
            data = {
                'username': user.username,
                'email': user.email,
                'direccion': user.direccion,
                'edad': user.edad,
                'ocupacion': user.ocupacion,
                'celular': user.celular,
                'acudiente': user.acudiente,
            }
            return JsonResponse(data)
    return JsonResponse({}, status=404)

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def eliminarhistorias(request, id):
    historiaseliminar = get_object_or_404(Valoracion, id=id)
    
    if request.method == 'POST':
        historiaseliminar.delete()
        return redirect('listhistorias')
    
    return redirect('listhistorias')

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def crearhistorias(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        user = UserProfile.objects.filter(numero=numero).first()
        
        formularioI = UserForm(request.POST)
        formularioII = ValoracionForm(request.POST)
        
        if user:
            formularioI = UserForm(request.POST, instance=user)
            if formularioI.is_valid() and formularioII.is_valid():
                user = formularioI.save()
                valoracion = formularioII.save(commit=False)
                valoracion.user = user
                valoracion.save()
                messages.success(request, 'Historia clínica creada con éxito.')
                return redirect('listhistorias')
            else:
                print("Errores en formularioI:", formularioI.errors)
                print("Errores en formularioII:", formularioII.errors)
        else:
            messages.error(request, 'El usuario no existe. Por favor, verifique el número ingresado.')
    else:
        formularioI = UserForm()
        formularioII = ValoracionForm()
    
    context = {
        'formularioI': formularioI,
        'formularioII': formularioII
    }
    return render(request, 'historiaclinica/crearhistorias.html', context)

def base(request):
    return render(request, 'index.html')

def loginregister(request):
    return render(request, 'loginregister.html')

def inicio(request):
    return render(request, 'inicio.html')

def signout(request):
    logout(request)
    return redirect('loginregister')

@login_required()
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html', {'user': request.user})
    else:
        return redirect('loginregister')

@login_required()
def configuracion(request, id):
    perfil_usuario = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=perfil_usuario)
        if form.is_valid():
            form.save()
            return redirect('dashboard') 
    else:
        form = UserForm(instance=perfil_usuario)
    return render(request, 'configuracion.html', {'form': form})

@login_required()
def crearcitas(request):
    return render(request, 'citas/crearcitas.html')

@login_required()
def listcitas(request):
    return render(request, 'citas/listcitas.html')

@login_required()
def editarcitas(request):
    return render(request, 'citas/editarcitas.html')

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def crearcuentas(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listcuentas')  
    else:
        form = UserForm()
    
    return render(request, 'cuentas/crearcuentas.html', {'form': form})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def listcuentas(request):
    cuentas= UserProfile.objects.all()
    return render(request, 'cuentas/listcuentas.html', {'cuentas': cuentas})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def editarcuentas(request, id):
    form_edcuentas = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=form_edcuentas)
        if form.is_valid():
            form.save()
            return redirect('listcuentas') 
    else:
        form = UserForm(instance=form_edcuentas)
    return render(request, 'cuentas/editarcuentas.html', {'form': form})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def eliminarelementos(request, id):
    elementoseliminar = get_object_or_404(Inventario, id=id)
    
    if request.method == 'POST':
        elementoseliminar.delete()
        return redirect('listelementos')
    
    return redirect('listelementos')

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def crearfechas(request):
    if request.method == 'POST':
        disponibilidad = FechaForm(request.POST)
        if disponibilidad.is_valid():
            disponibilidad.save()
            return redirect('listfechas')
    else:
        form = FechaForm()
    
    return render(request, 'fechas/crearfechas.html', {'form': form})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def listfechas(request):
    disponibilidades= Fecha.objects.all()
    return render(request, 'fechas/listfechas.html', {'disponibilidades': disponibilidades})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def editarfechas(request, id):
    disponibilidad = Fecha.objects.get(id=id)
    if request.method == 'POST':
        form = FechaForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            form.save()
            return redirect('listfechas')
    else:
        form = FechaForm(instance=disponibilidad)
    return render(request, 'fechas/editarfechas.html', {'form': form})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required
def eliminarfechas(request, id):
    fechaseliminar = get_object_or_404(Fecha, id=id)
    
    if request.method == 'POST':
        fechaseliminar.delete()
        return redirect('listfechas')
    
    return redirect('listfechas')

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def crearelementos(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listelementos')  
    else:
        form = InventarioForm()
    
    return render(request, 'inventario/crearelementos.html', {'form': form})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def listelementos(request):
    inventarios= Inventario.objects.all()
    return render(request, 'inventario/listelementos.html', {'inventarios': inventarios})

@user_passes_test(es_superusuario, login_url='acceso_denegado')
@login_required()
def editarelementos(request, id):
    form_edelem = Inventario.objects.get(id=id)
    if request.method == 'POST':
        form = InventarioForm(request.POST, request.FILES, instance=form_edelem)
        if form.is_valid():
            form.save()
            return redirect('listelementos') 
    else:
        form = InventarioForm(instance=form_edelem)
    return render(request, 'inventario/editarelementos.html', {'form': form})

@login_required()
def correo(request):
    return render(request, 'correo.html')

@login_required()
def calendario(request):
    return render(request, 'calendario.html')