import imgImageNirvamiLogo from "figma:asset/34629939463a62914e4d6cf8617751092b770df0.png";

function Button() {
  return (
    <div className="h-[24px] relative shrink-0 w-[41.962px]" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[41.962px]">
        <p className="absolute font-['Arial:Regular',sans-serif] leading-[24px] left-0 not-italic text-[#364153] text-[16px] text-nowrap top-[-2.2px] whitespace-pre">Menu</p>
      </div>
    </div>
  );
}

function Button1() {
  return (
    <div className="basis-0 grow h-[24px] min-h-px min-w-px relative shrink-0" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-full">
        <p className="absolute font-['Arial:Regular',sans-serif] leading-[24px] left-0 not-italic text-[#364153] text-[16px] text-nowrap top-[-2.2px] whitespace-pre">About</p>
      </div>
    </div>
  );
}

function Container() {
  return (
    <div className="h-[24px] relative shrink-0 w-[111.025px]" data-name="Container">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[24px] h-[24px] items-center relative w-[111.025px]">
        <Button />
        <Button1 />
      </div>
    </div>
  );
}

function Button2() {
  return (
    <div className="h-[20px] relative shrink-0 w-[32px]" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[20px] relative w-[32px]">
        <p className="absolute font-['Arial:Bold',sans-serif] leading-[20px] left-0 not-italic text-[#364153] text-[14px] text-nowrap top-[-1.2px] whitespace-pre">Yoga</p>
      </div>
    </div>
  );
}

function Button3() {
  return (
    <div className="h-[20px] relative shrink-0 w-[62.925px]" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[20px] relative w-[62.925px]">
        <p className="absolute font-['Arial:Bold',sans-serif] leading-[20px] left-0 not-italic text-[#364153] text-[14px] text-nowrap top-[-1.2px] whitespace-pre">Ayurveda</p>
      </div>
    </div>
  );
}

function Button4() {
  return (
    <div className="bg-[#009966] h-[32px] relative rounded-[8px] shrink-0 w-[104.138px]" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[6px] h-[32px] items-center justify-center px-[16px] py-0 relative w-[104.138px]">
        <p className="font-['Arial:Regular',sans-serif] leading-[20px] not-italic relative shrink-0 text-[14px] text-nowrap text-white whitespace-pre">Get Started</p>
      </div>
    </div>
  );
}

function Container1() {
  return (
    <div className="h-[32px] relative shrink-0 w-[231.062px]" data-name="Container">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[16px] h-[32px] items-center relative w-[231.062px]">
        <Button2 />
        <Button3 />
        <Button4 />
      </div>
    </div>
  );
}

function LandingPage() {
  return (
    <div className="absolute box-border content-stretch flex h-[80px] items-center justify-between left-0 px-[16px] py-0 top-0 w-[1208.8px]" data-name="LandingPage">
      <Container />
      <Container1 />
    </div>
  );
}

function ImageNirvamiLogo() {
  return (
    <div className="absolute h-[80px] left-[0.6px] top-[-8px] w-[72px]" data-name="Image (Nirvami Logo)">
      <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgImageNirvamiLogo} />
    </div>
  );
}

function Text() {
  return (
    <div className="absolute h-[20px] left-[5.66px] top-[60px] w-[60.675px]" data-name="Text">
      <p className="absolute font-['Arial:Regular',sans-serif] leading-[20px] left-[0.94px] not-italic text-[#101828] text-[14px] text-nowrap top-[-4px] tracking-[0.7px] uppercase whitespace-pre">NIRVAMI</p>
    </div>
  );
}

function LandingPage1() {
  return (
    <div className="absolute h-[80px] left-[568.4px] top-0 w-[72px]" data-name="LandingPage">
      <ImageNirvamiLogo />
      <Text />
    </div>
  );
}

export default function Navigation() {
  return (
    <div className="bg-[rgba(245,230,211,0.95)] relative shadow-[0px_1px_3px_0px_rgba(0,0,0,0.1),0px_1px_2px_-1px_rgba(0,0,0,0.1)] size-full" data-name="Navigation">
      <LandingPage />
      <LandingPage1 />
    </div>
  );
}