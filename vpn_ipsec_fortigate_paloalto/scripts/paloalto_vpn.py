from panos.network import (
    TunnelInterface,
    IkeGateway,
    IpsecTunnel,
    IpsecCryptoProfile,
    IkeCryptoProfile,
    Zone,
    StaticRoute,
    VirtualRouter,
)
from panos.policies import SecurityRule, Rulebase
import config_vpn


def criar_interface_tunel(firewall):
    """
    Cria a interface de túnel (tunnel.1) no Palo Alto, com o IP definido
    em config_vpn.PALOALTO_TUNNEL_IP.
    """
    tunnel = TunnelInterface(
        name="tunnel.1",
        ip=[f"{config_vpn.PALOALTO_TUNNEL_IP}/30"],
    )
    firewall.add(tunnel)
    tunnel.create()
    return tunnel


def criar_zona_e_associar_interface(firewall):
    """
    Cria a zona de segurança para o túnel e associa a interface criada
    anteriormente. No Palo Alto, toda interface precisa pertencer a uma
    zona para que o tráfego seja processado pelas políticas.
    """
    zona = Zone(
        name="VPN-ZONE",
        mode="layer3",
        interface=["tunnel.1"],
    )
    firewall.add(zona)
    zona.create()
    return zona


def criar_ike_crypto_profile(firewall):
    """
    Cria o perfil de criptografia IKE (equivalente à proposta de Phase 1
    do FortiGate).
    """
    proposta = config_vpn.PHASE1_PROPOSAL
    perfil = IkeCryptoProfile(
        name=config_vpn.TUNNEL_NAME,
        dh_group=[f"group{proposta['dh_group']}"],
        authentication=[proposta["hash"]],
        encryption=[proposta["encryption"]],
        lifetime_seconds=proposta["lifetime_seconds"],
    )
    firewall.add(perfil)
    perfil.create()
    return perfil


def criar_ike_gateway(firewall):
    """
    Cria o IKE Gateway (equivalente à Phase 1 do FortiGate), definindo
    o peer remoto (FortiGate) e associando o perfil de criptografia.

    Nota: local_ip_address precisa incluir a máscara de rede (/30),
    igual ao IP configurado na interface ethernet1/2 - o Palo Alto exige
    correspondência exata com o endereço já atribuído à interface.
    """
    gateway = IkeGateway(
        name=config_vpn.TUNNEL_NAME,
        version="ikev2",
        interface="ethernet1/2",
        local_ip_address_type="ip",
        local_ip_address=f"{config_vpn.PALOALTO_WAN_IP}/30",
        peer_ip_type="ip",
        peer_ip_value=config_vpn.FORTIGATE_WAN_IP,
        auth_type="pre-shared-key",
        pre_shared_key=config_vpn.IPSEC_PSK,
        ikev2_crypto_profile=config_vpn.TUNNEL_NAME,
    )
    firewall.add(gateway)
    gateway.create()
    return gateway


def criar_ipsec_crypto_profile(firewall):
    """
    Cria o perfil de criptografia IPSec (equivalente à proposta de
    Phase 2 do FortiGate), incluindo PFS.
    """
    proposta = config_vpn.PHASE2_PROPOSAL
    perfil = IpsecCryptoProfile(
        name=config_vpn.TUNNEL_NAME,
        esp_encryption=[proposta["encryption"]],
        esp_authentication=[proposta["authentication"]],
        dh_group=f"group{proposta['pfs_group']}",
        lifetime_seconds=proposta["lifetime_seconds"],
    )
    firewall.add(perfil)
    perfil.create()
    return perfil


def criar_ipsec_tunnel(firewall):
    """
    Cria o IPSec Tunnel (equivalente à Phase 2 do FortiGate), associando
    a interface de túnel, o IKE Gateway e o perfil de criptografia IPSec.
    """
    tunel = IpsecTunnel(
        name=config_vpn.TUNNEL_NAME,
        tunnel_interface="tunnel.1",
        ak_ike_gateway=config_vpn.TUNNEL_NAME,
        ak_ipsec_crypto_profile=config_vpn.TUNNEL_NAME,
    )
    firewall.add(tunel)
    tunel.create()
    return tunel


def criar_rota_estatica(firewall):
    """
    Cria a rota estática apontando o tráfego destinado à rede remota
    (FortiGate) para a interface de túnel, associada ao virtual router
    "default". O next-hop é o IP do FortiGate na rede de túnel
    (169.255.1.0/30) - o "vizinho direto" do outro lado do túnel P2P.

    Antes de criar a rota, associa a interface tunnel.1 ao virtual
    router - lendo a lista de interfaces já existentes (ethernet1/2,
    ethernet1/3) e adicionando tunnel.1 a essa lista, sem remover as
    demais.
    """
    vr = VirtualRouter(name="default")
    firewall.add(vr)
    vr.refresh()

    interfaces_atuais = list(vr.interface) if vr.interface else []
    if "tunnel.1" not in interfaces_atuais:
        interfaces_atuais.append("tunnel.1")
        vr.interface = interfaces_atuais
        vr.apply()

    rota = StaticRoute(
        name=config_vpn.TUNNEL_NAME,
        destination=config_vpn.FORTIGATE_LOCAL_NETWORK,
        interface="tunnel.1",
        nexthop_type="ip-address",
        nexthop=config_vpn.FORTIGATE_TUNNEL_IP,
    )
    vr.add(rota)
    rota.create()
    return rota


def criar_politica_seguranca(firewall):
    """
    Cria as políticas de segurança permitindo tráfego bidirecional entre
    a zona LAN (LAN-ZONE) e a zona do túnel (VPN-ZONE).

    Nota: assume que a zona "LAN-ZONE" já existe (criada ao configurar
    a interface ethernet1/1). Caso ainda não exista, esta etapa falhará
    até que a LAN seja configurada.
    """
    rulebase = Rulebase()
    firewall.add(rulebase)

    regra_saida = SecurityRule(
        name=f"{config_vpn.TUNNEL_NAME}_OUT",
        fromzone=["LAN-ZONE"],
        tozone=["VPN-ZONE"],
        source=["any"],
        destination=["any"],
        application=["any"],
        service=["any"],
        action="allow",
    )

    regra_entrada = SecurityRule(
        name=f"{config_vpn.TUNNEL_NAME}_IN",
        fromzone=["VPN-ZONE"],
        tozone=["LAN-ZONE"],
        source=["any"],
        destination=["any"],
        application=["any"],
        service=["any"],
        action="allow",
    )

    rulebase.add(regra_saida)
    rulebase.add(regra_entrada)
    regra_saida.create()
    regra_entrada.create()

    return regra_saida, regra_entrada


def configurar_vpn_completa(firewall):
    """
    Executa todos os passos necessários para configurar a VPN no Palo
    Alto, seguindo a ordem: interface -> zona -> perfis de criptografia
    -> IKE Gateway -> IPSec Tunnel -> rota -> políticas -> commit.
    Retorna um dicionário indicando sucesso/erro em cada etapa.
    """
    resultados = {}

    try:
        criar_interface_tunel(firewall)
        resultados["interface_tunel"] = "OK"
    except Exception as erro:
        resultados["interface_tunel"] = f"ERRO: {erro}"

    try:
        criar_zona_e_associar_interface(firewall)
        resultados["zona"] = "OK"
    except Exception as erro:
        resultados["zona"] = f"ERRO: {erro}"

    try:
        criar_ike_crypto_profile(firewall)
        resultados["ike_crypto_profile"] = "OK"
    except Exception as erro:
        resultados["ike_crypto_profile"] = f"ERRO: {erro}"

    try:
        criar_ike_gateway(firewall)
        resultados["ike_gateway"] = "OK"
    except Exception as erro:
        resultados["ike_gateway"] = f"ERRO: {erro}"

    try:
        criar_ipsec_crypto_profile(firewall)
        resultados["ipsec_crypto_profile"] = "OK"
    except Exception as erro:
        resultados["ipsec_crypto_profile"] = f"ERRO: {erro}"

    try:
        criar_ipsec_tunnel(firewall)
        resultados["ipsec_tunnel"] = "OK"
    except Exception as erro:
        resultados["ipsec_tunnel"] = f"ERRO: {erro}"

    try:
        criar_rota_estatica(firewall)
        resultados["rota_estatica"] = "OK"
    except Exception as erro:
        resultados["rota_estatica"] = f"ERRO: {erro}"

    try:
        criar_politica_seguranca(firewall)
        resultados["politica_seguranca"] = "OK"
    except Exception as erro:
        resultados["politica_seguranca"] = f"ERRO: {erro}"

    try:
        firewall.commit(sync=True)
        resultados["commit"] = "OK"
    except Exception as erro:
        resultados["commit"] = f"ERRO: {erro}"

    return resultados