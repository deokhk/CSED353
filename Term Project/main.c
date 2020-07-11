#include <sys/time.h>
#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#include <net/ethernet.h>
#include <pcap/pcap.h>
#include <stdio.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>
#include <stdbool.h>


struct ip *ip_header;
struct tcphdr *tcp_header;
struct udphdr *udp_header;
struct icmphdr *icmp_header;

long initial_sec = 0;
long initial_usec= 0;

void got_packet(u_char *param, const struct pcap_pkthdr *hdr, const u_char *packet);
void concat_mac(const u_int8_t *s_addr,const u_int8_t *d_addr, char* msg);
void concat_ip(char* msg);

int main(int argc, char *argv[]){

  pcap_if_t *alldev_list; // pointer value to the list where we store a list of network devices(interfaces)
  pcap_if_t *dev; // dev pointer
  char errbuf[PCAP_ERRBUF_SIZE]; // buffer to store error messages
  int num = 0;
  int interface_num= 0;
  bool is_valid_interface_num = true;
  pcap_t *handle;
  int bufsize = 65536; // buffer size
  int cnt = 0; // # of packet user want to process


  /* Get the device list(interfaces) from the local machine*/
  if(pcap_findalldevs(&alldev_list, errbuf) == -1){
    // if error, record error in errbuf
    fprintf(stderr,"Error in pcap_findalldevs: %s\n", errbuf);
    return -1;
  }

  for(dev=alldev_list; dev; dev=dev->next){
    printf("%d: %s ", ++num, dev-> name); // print dev interface number, name
    if(dev->description){
      printf("(%s)\n", dev->description); // if description available, show description
    }
    else{
      printf("(No description available)\n");
    }
  }

  if(num == 0){
    //No interface is detected, then return -1
    printf("No interfaces Found!\n");
    return -1;
  }

  do {
    printf("Select the interface number (1-%d): ",num); // Prompt user to select the interface
    scanf("%d", &interface_num); //
    if(!(1 <= interface_num && interface_num <= num)){
      is_valid_interface_num = false;
      printf("Typed interface number is not in valid range. Type again.\n");
    }
    else{
      is_valid_interface_num = true;
    }
  } while(!is_valid_interface_num);


  num = 1;
  for(dev=alldev_list; num < interface_num; dev=dev->next); // List traversal to find the target interface.

  /*Open the session in promiscuous mode */

  handle = pcap_open_live(dev->name, bufsize, 1, 1000, errbuf); /// Open the device
  if(handle == NULL){
    fprintf(stderr, "Couldn't open device %s: %s\n", dev->name, errbuf); // if error occurs, record that error message to errbuf.
    return -1;
  }

  printf("Selected device %s is available\n", dev->name);

  printf("How many packet do you want to process?\n If you want to process infinity packets, type 0 : ");
  scanf("%d", &cnt);

  pcap_loop(handle, cnt, got_packet, NULL);

  pcap_close(handle);

  return 0;
}
void got_packet(u_char *param, const struct pcap_pkthdr *hdr, const u_char *packet){

  /*Show the packet arrival time*/
  long arrival_sec = hdr->ts.tv_sec;
  long arrival_usec = hdr->ts.tv_usec;
  long arrival_relative_sec = 0;
  long arrival_relative_usec = 0;

  unsigned short ethernet_type;
  const struct ether_header *ethernet_header;
  char msg[1024]="";
  char buf[100]; 

  if(initial_sec==0){
    initial_sec = arrival_sec;
    initial_usec = arrival_usec;
  }

  if(arrival_usec >= initial_usec){
    arrival_relative_sec = arrival_sec - initial_sec;
    arrival_relative_usec = arrival_usec - initial_usec;
  }
  else{
    arrival_relative_sec = arrival_sec-1-initial_sec;
    arrival_relative_usec = arrival_usec + 1000000 - initial_usec;
  }
  sprintf(buf, "%ld.%ld: ",arrival_relative_sec, arrival_relative_usec);
  strcat(msg,buf);
  

  /*Get ethernet header and print MAC info*/
  ethernet_header = (struct ether_header *)packet;
  concat_mac(ethernet_header->ether_shost, ethernet_header->ether_dhost,msg);

  /*Get Ip header and print IP info*/
  ethernet_type = ntohs(ethernet_header->ether_type);
  if(ethernet_type == ETHERTYPE_IP){
    //This packet is ip packet.
    ip_header = (struct ip *)(packet + sizeof(struct ether_header)); // size of ethernet header is always 14.
    concat_ip(msg); // print ip src and dst addr.

    if(ip_header->ip_p == IPPROTO_TCP){
      /*Protocol is TCP*/
      strcat(msg," TCP ");
      tcp_header = (struct tcphdr *)(packet + sizeof(struct ether_header) + ip_header->ip_hl * 4);
      sprintf(buf, "Src Port: %d, Dst Port: %d, Seq Num: %d, Ack Num: %d", ntohs(tcp_header->th_sport), ntohs(tcp_header->th_dport), ntohs(tcp_header->th_seq), ntohs(tcp_header->th_ack));
      strcat(msg,buf);
      printf("\033[1;36m %s\n",msg);
    }
    else if(ip_header->ip_p == IPPROTO_UDP){
      /*Protocol is UDP*/
      strcat(msg," UDP ");
      udp_header = (struct udphdr *)(packet + sizeof(struct ether_header) + ip_header->ip_hl * 4);
      sprintf(buf, "Src Port: %d, Dst Port: %d", ntohs(udp_header->uh_sport), ntohs(udp_header->uh_dport));
      strcat(msg,buf);

      printf("\033[1;32m %s\n",msg);
    }
    else if(ip_header->ip_p == IPPROTO_ICMP){
      /*Protocol is ICMP*/
      strcat(msg," ICMP ");
      icmp_header = (struct icmphdr *)(packet + sizeof(struct ether_header) + ip_header->ip_hl * 4);
      sprintf(buf, "Type: %d, Code: %d", ntohs(icmp_header->type), ntohs(icmp_header->code));
      strcat(msg,buf);
      printf("\033[1;33m %s\n",msg);
    }
    else{
      strcat(msg," OTHER TYPE ");
      printf("\033[0;32m %s\n",msg);
    }
    
  }
  else{
    printf("\033[0;34m This packet is not an IP packet.\n");
  }
}

void concat_mac(const u_int8_t *s_addr,const u_int8_t *d_addr, char* msg){

  /*Convert mac address in appropriate string format and concatenate it to msg*/
  char buf[100];
  int size_of_mac = 6; // mac address is 48 bit
  int i=0;
  strcat(msg,"[");
  for(i=0; i<size_of_mac; i++){
    sprintf(buf,"%02x", s_addr[i]);
    strcat(msg,buf);
    if(i!=size_of_mac-1){
      strcat(msg,":");
    }
  }
  strcat(msg,"->");

  i=0;
  for(i=0; i<size_of_mac; i++){
    sprintf(buf,"%02x", d_addr[i]);
    strcat(msg,buf);
    if(i!=size_of_mac-1){
      strcat(msg, ":");
    }
  }
  strcat(msg, "]");
}

void concat_ip(char* msg){
  /*Convert mac address in appropriate string format and concatenate it to msg*/
  char buf[100];
  strcat(msg, "(");
  sprintf(buf,"%s", inet_ntoa(ip_header->ip_src));
  strcat(msg,buf);
  strcat(msg, "->");
  sprintf(buf,"%s", inet_ntoa(ip_header->ip_dst));
  strcat(msg,buf);
  strcat(msg, ") ");
}
